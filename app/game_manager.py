import asyncio
import time
import json
import logging
from typing import Dict, Any, Optional
from app.database import (
    create_or_get_session, 
    register_participant, 
    record_answer, 
    finish_session_in_db
)
from app.questions_data import ZOHO_RECRUIT_QUESTIONS

logger = logging.getLogger("recruit_arena.game")

class Room:
    def __init__(self, room_code: str, title: str = "Zoho Recruit: Cyber-Talent Arena"):
        self.room_code = room_code
        self.title = title
        self.status = "LOBBY"  # LOBBY, INTRO, QUESTION, REVEAL, LEADERBOARD, PODIUM
        self.host_ws = None
        self.players: Dict[str, Dict[str, Any]] = {}
        self.questions = ZOHO_RECRUIT_QUESTIONS
        self.current_q_index = -1
        self.q_start_time = 0.0
        self.timer_task: Optional[asyncio.Task] = None
        self.lock = asyncio.Lock()
        self.session_db_record = None

    @property
    def current_question(self) -> Optional[Dict[str, Any]]:
        if 0 <= self.current_q_index < len(self.questions):
            return self.questions[self.current_q_index]
        return None

    def get_ranked_players(self):
        return sorted(
            self.players.values(), 
            key=lambda p: (p["score"], p["correct_answers"]), 
            reverse=True
        )

class GameManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}

    def get_or_create_room(self, room_code: str) -> Room:
        room_code = room_code.upper().strip()
        if room_code not in self.rooms:
            room = Room(room_code)
            # Create session in Supabase
            try:
                room.session_db_record = create_or_get_session(room_code, room.title)
            except Exception as e:
                logger.error(f"Failed to record session in DB: {e}")
            self.rooms[room_code] = room
        return self.rooms[room_code]

    def get_room(self, room_code: str) -> Optional[Room]:
        return self.rooms.get(room_code.upper().strip())

    async def register_player(self, room_code: str, full_name: str, email: str, role_or_area: str, nickname: str, avatar: str):
        room = self.get_or_create_room(room_code)
        async with room.lock:
            # Register in Supabase
            db_player = None
            try:
                db_player = register_participant(room.room_code, full_name, email, role_or_area, nickname, avatar)
            except Exception as e:
                logger.error(f"Failed to register participant in Supabase: {e}")

            player_id = str(db_player["id"]) if db_player else f"p_{int(time.time()*1000)}"

            player_obj = {
                "id": player_id,
                "full_name": full_name,
                "email": email,
                "role_or_area": role_or_area,
                "nickname": nickname,
                "avatar": avatar or "cyber_scout",
                "score": 0,
                "streak": 0,
                "correct_answers": 0,
                "total_answered": 0,
                "current_answer": None,
                "current_response_time_ms": 0,
                "last_points": 0,
                "ws": None,
                "connected": True
            }
            room.players[player_id] = player_obj

            # Broadcast update to Host
            await self._notify_host_player_joined(room, player_obj)
            return player_obj

    async def attach_ws(self, room_code: str, client_type: str, client_id: str, ws):
        room = self.get_or_create_room(room_code)
        if client_type == "host":
            room.host_ws = ws
            # Send current room state to host
            await ws.send_text(json.dumps({
                "type": "ROOM_STATE",
                "status": room.status,
                "room_code": room.room_code,
                "players": [self._clean_player(p) for p in room.players.values()],
                "current_q_index": room.current_q_index,
                "total_questions": len(room.questions)
            }))
        else:
            player = room.players.get(client_id)
            if player:
                player["ws"] = ws
                player["connected"] = True
                await ws.send_text(json.dumps({
                    "type": "JOIN_SUCCESS",
                    "player": self._clean_player(player),
                    "room_status": room.status,
                    "current_q_index": room.current_q_index
                }))
                if room.status == "QUESTION":
                    # Send active question format to player
                    await self._send_question_to_player(room, player)

    async def detach_ws(self, room_code: str, client_type: str, client_id: str):
        room = self.get_room(room_code)
        if not room:
            return
        if client_type == "host":
            room.host_ws = None
        else:
            player = room.players.get(client_id)
            if player:
                player["ws"] = None
                player["connected"] = False
                if room.host_ws:
                    try:
                        await room.host_ws.send_text(json.dumps({
                            "type": "PLAYER_DISCONNECTED",
                            "player_id": client_id
                        }))
                    except Exception:
                        pass

    async def start_game(self, room_code: str):
        room = self.get_room(room_code)
        if not room:
            return
        async with room.lock:
            room.current_q_index = 0
            await self._launch_question(room)

    async def next_question(self, room_code: str):
        room = self.get_room(room_code)
        if not room:
            return
        async with room.lock:
            if room.timer_task and not room.timer_task.done():
                room.timer_task.cancel()
            room.current_q_index += 1
            if room.current_q_index < len(room.questions):
                await self._launch_question(room)
            else:
                await self._trigger_podium(room)

    async def _launch_question(self, room: Room):
        q = room.current_question
        if not q:
            return

        room.status = "QUESTION"
        room.q_start_time = time.time()
        for p in room.players.values():
            p["current_answer"] = None
            p["current_response_time_ms"] = 0
            p["last_points"] = 0

        # Host receives full question + metadata
        if room.host_ws:
            try:
                await room.host_ws.send_text(json.dumps({
                    "type": "QUESTION_START",
                    "question_index": room.current_q_index,
                    "total_questions": len(room.questions),
                    "question": q,
                    "players_count": len([p for p in room.players.values() if p["connected"]])
                }))
            except Exception as e:
                logger.error(f"Error sending QUESTION_START to host: {e}")

        # Players receive interactive question
        for p in room.players.values():
            await self._send_question_to_player(room, p)

        # Start countdown timer in background
        if room.timer_task and not room.timer_task.done():
            room.timer_task.cancel()
        room.timer_task = asyncio.create_task(self._run_timer(room, q["time_limit_sec"]))

    async def _send_question_to_player(self, room: Room, player: Dict[str, Any]):
        if not player["ws"]:
            return
        q = room.current_question
        if not q:
            return
        # Strip correct answers when sending to player
        clean_q = {
            "id": q["id"],
            "order_num": q["order_num"],
            "type": q["type"],
            "category": q["category"],
            "title": q["title"],
            "question_text": q["question_text"],
            "options": q["options"],
            "time_limit_sec": q["time_limit_sec"]
        }
        try:
            await player["ws"].send_text(json.dumps({
                "type": "QUESTION_ACTIVE",
                "question": clean_q,
                "question_index": room.current_q_index,
                "total_questions": len(room.questions)
            }))
        except Exception as e:
            logger.error(f"Error sending question to player {player['id']}: {e}")

    async def _run_timer(self, room: Room, duration: int):
        try:
            for remaining in range(duration, -1, -1):
                # Broadcast timer tick to host and players
                tick_msg = json.dumps({"type": "TIMER_TICK", "remaining": remaining, "duration": duration})
                if room.host_ws:
                    try:
                        await room.host_ws.send_text(tick_msg)
                    except Exception:
                        pass
                for p in room.players.values():
                    if p["ws"]:
                        try:
                            await p["ws"].send_text(tick_msg)
                        except Exception:
                            pass
                if remaining == 0:
                    break
                await asyncio.sleep(1)
            
            # When time expires, reveal results
            await self.reveal_results(room.room_code)
        except asyncio.CancelledError:
            pass

    async def submit_answer(self, room_code: str, player_id: str, answer_payload: Any):
        room = self.get_room(room_code)
        if not room or room.status != "QUESTION":
            return
        
        async with room.lock:
            player = room.players.get(player_id)
            if not player or player["current_answer"] is not None:
                return  # Already answered or invalid

            now = time.time()
            elapsed_sec = max(0.1, now - room.q_start_time)
            response_time_ms = int(elapsed_sec * 1000)

            q = room.current_question
            is_correct = False
            points = 0

            if q["type"] == "ORDER_SEQUENCE":
                # answer_payload is expected to be list of option ids: ['opt_A', 'opt_B', 'opt_C', 'opt_D']
                is_correct = (answer_payload == q["correct_order"])
            else:
                # answer_payload is string option id
                is_correct = (answer_payload == q.get("correct_answer"))

            if is_correct:
                player["streak"] += 1
                base_points = q.get("points_base", 1000)
                time_ratio = min(1.0, elapsed_sec / q["time_limit_sec"])
                speed_score = round(base_points * (1 - (time_ratio * 0.5)))
                streak_bonus = min(500, player["streak"] * 100)
                points = speed_score + streak_bonus
                player["score"] += points
                player["correct_answers"] += 1
            else:
                player["streak"] = 0
                points = 0

            player["total_answered"] += 1
            player["current_answer"] = answer_payload
            player["current_response_time_ms"] = response_time_ms
            player["last_points"] = points

            # Record answer asynchronously in Supabase
            session_id = room.session_db_record["id"] if room.session_db_record else None
            try:
                record_answer(
                    session_id=session_id,
                    participant_id=player["id"],
                    question_id=q["id"],
                    chosen_answer=answer_payload,
                    is_correct=is_correct,
                    response_time_ms=response_time_ms,
                    points_awarded=points,
                    new_streak=player["streak"],
                    new_score=player["score"]
                )
            except Exception as e:
                logger.error(f"Error persisting answer in Supabase: {e}")

            # Notify player immediately that their submission was received
            if player["ws"]:
                try:
                    await player["ws"].send_text(json.dumps({
                        "type": "ANSWER_ACKNOWLEDGED",
                        "is_correct": is_correct,
                        "points_earned": points,
                        "streak": player["streak"],
                        "total_score": player["score"]
                    }))
                except Exception:
                    pass

            # Update Host with answer count
            answered_count = len([p for p in room.players.values() if p["current_answer"] is not None])
            active_count = len([p for p in room.players.values() if p["connected"]])
            if room.host_ws:
                try:
                    await room.host_ws.send_text(json.dumps({
                        "type": "ANSWER_RECEIVED_COUNT",
                        "answered": answered_count,
                        "total": active_count
                    }))
                except Exception:
                    pass

            # If all connected players have answered, conclude timer early!
            if answered_count >= active_count and active_count > 0:
                if room.timer_task and not room.timer_task.done():
                    room.timer_task.cancel()
                asyncio.create_task(self.reveal_results(room.room_code))

    async def reveal_results(self, room_code: str):
        room = self.get_room(room_code)
        if not room or room.status == "REVEAL":
            return
        async with room.lock:
            room.status = "REVEAL"
            q = room.current_question
            if not q:
                return

            # Compute answer distribution for Host chart
            distribution = {}
            for opt in q["options"]:
                distribution[opt["id"]] = 0
            for p in room.players.values():
                ans = p["current_answer"]
                if ans is not None:
                    if isinstance(ans, list) and len(ans) > 0:
                        distribution[ans[0]] = distribution.get(ans[0], 0) + 1
                    elif isinstance(ans, str):
                        distribution[ans] = distribution.get(ans, 0) + 1

            reveal_payload = {
                "type": "REVEAL_RESULTS",
                "question": q,
                "distribution": distribution,
                "correct_answer": q.get("correct_order") or q.get("correct_answer"),
                "explanation": q.get("explanation", ""),
                "players_answered": len([p for p in room.players.values() if p["current_answer"] is not None])
            }

            if room.host_ws:
                try:
                    await room.host_ws.send_text(json.dumps(reveal_payload))
                except Exception:
                    pass

            # Notify each player of round outcome
            ranked = room.get_ranked_players()
            for rank_idx, p in enumerate(ranked, start=1):
                if p["ws"]:
                    try:
                        await p["ws"].send_text(json.dumps({
                            "type": "ROUND_FEEDBACK",
                            "is_correct": (p["last_points"] > 0),
                            "points_earned": p["last_points"],
                            "total_score": p["score"],
                            "rank": rank_idx,
                            "streak": p["streak"],
                            "correct_answer": q.get("correct_order") or q.get("correct_answer"),
                            "explanation": q.get("explanation", "")
                        }))
                    except Exception:
                        pass

    async def show_leaderboard(self, room_code: str):
        room = self.get_room(room_code)
        if not room:
            return
        async with room.lock:
            room.status = "LEADERBOARD"
            top_players = [self._clean_player(p) for p in room.get_ranked_players()[:10]]
            leaderboard_msg = json.dumps({
                "type": "LEADERBOARD_UPDATE",
                "leaderboard": top_players,
                "question_index": room.current_q_index,
                "total_questions": len(room.questions)
            })

            if room.host_ws:
                try:
                    await room.host_ws.send_text(leaderboard_msg)
                except Exception:
                    pass

            for p in room.players.values():
                if p["ws"]:
                    try:
                        await p["ws"].send_text(leaderboard_msg)
                    except Exception:
                        pass

    async def _trigger_podium(self, room: Room):
        room.status = "PODIUM"
        ranked = room.get_ranked_players()
        podium_players = [self._clean_player(p) for p in ranked[:3]]
        full_rankings = [self._clean_player(p) for p in ranked]

        # Finalize session in Supabase
        try:
            finish_session_in_db(room.room_code, ranked)
        except Exception as e:
            logger.error(f"Error updating final ranks in Supabase: {e}")

        podium_msg = json.dumps({
            "type": "FINAL_PODIUM",
            "podium": podium_players,
            "all_players": full_rankings
        })

        if room.host_ws:
            try:
                await room.host_ws.send_text(podium_msg)
            except Exception:
                pass

        for rank_idx, p in enumerate(ranked, start=1):
            if p["ws"]:
                try:
                    await p["ws"].send_text(json.dumps({
                        "type": "FINAL_PODIUM_PLAYER",
                        "final_rank": rank_idx,
                        "total_score": p["score"],
                        "podium": podium_players
                    }))
                except Exception:
                    pass

    async def _notify_host_player_joined(self, room: Room, player: Dict[str, Any]):
        if room.host_ws:
            try:
                await room.host_ws.send_text(json.dumps({
                    "type": "PLAYER_JOINED",
                    "player": self._clean_player(player),
                    "total_players": len(room.players)
                }))
            except Exception as e:
                logger.error(f"Error notifying host: {e}")

    def _clean_player(self, p: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": p["id"],
            "full_name": p["full_name"],
            "email": p["email"],
            "role_or_area": p["role_or_area"],
            "nickname": p["nickname"],
            "avatar": p["avatar"],
            "score": p["score"],
            "streak": p["streak"],
            "correct_answers": p["correct_answers"],
            "total_answered": p["total_answered"],
            "connected": p["connected"]
        }

game_manager = GameManager()
