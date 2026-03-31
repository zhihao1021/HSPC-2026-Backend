from asyncpg.exceptions import PostgresError
from fastapi import APIRouter

from auth import UserIdDepends
from database import ConnDepends
from model.team import TeamCreate, TeamRead, TeamUpdate
from model.user import UserRead
from schemas.team import Team
from schemas.user import User

from .exceptions import (
    ALREADY_IN_TEAM,
    TEAM_IS_FULL,
    TEAM_NOT_FOUND,
    TEAM_NAME_ALREADY_EXISTS
)

router = APIRouter(
    prefix="/team",
    tags=["Team Management"],
)


@router.get("")
async def get_team_info(conn: ConnDepends, user_id: UserIdDepends) -> TeamRead:
    team_read = await Team.get_by_member_uid(
        conn=conn,
        member_uid=user_id,
        model_cls=TeamRead
    )

    if team_read is None:
        raise TEAM_NOT_FOUND

    return team_read


@router.post("")
async def create_team(
    conn: ConnDepends,
    user_id: UserIdDepends,
    data: TeamCreate
) -> TeamRead:
    if await User.check_have_team_by_uid(conn=conn, uid=user_id):
        raise ALREADY_IN_TEAM
    if await Team.exists_by_name(conn=conn, name=data.name):
        raise TEAM_NAME_ALREADY_EXISTS

    async with conn.transaction() as trans:
        team = Team(name=data.name)
        await team.save(conn=conn)
        await User.update_team_id_by_uid(conn=conn, uid=user_id, team_id=team.uid)

    return team.to_model(TeamRead)


@router.put("")
async def update_team_info(
    conn: ConnDepends,
    user_id: UserIdDepends,
    data: TeamUpdate
) -> TeamRead:
    team_uid = await User.get_team_id_by_uid(conn=conn, uid=user_id)

    if team_uid is None:
        raise TEAM_NOT_FOUND
    if data.name and await Team.exists_by_name(conn=conn, name=data.name):
        raise TEAM_NAME_ALREADY_EXISTS

    result = await Team.update_by_uid(
        conn=conn,
        uid=team_uid,
        data=data.model_dump(exclude_unset=True),
        return_result=True,
        model_cls=TeamRead
    )
    if result is None:
        raise TEAM_NOT_FOUND

    return result


@router.delete("")
async def leave_team(conn: ConnDepends, user_id: UserIdDepends) -> None:
    team_uid = await User.get_team_id_by_uid(conn=conn, uid=user_id)

    if team_uid is None:
        raise TEAM_NOT_FOUND

    async with conn.transaction():
        await User.update_team_id_by_uid(conn=conn, uid=user_id, team_id=None)


@router.put("/{team_uid}")
async def join_team(
    conn: ConnDepends,
    user_id: UserIdDepends,
    team_uid: str
) -> TeamRead:
    if await User.check_have_team_by_uid(conn=conn, uid=user_id):
        raise ALREADY_IN_TEAM

    team = await Team.get_by_uid(conn=conn, uid=team_uid)

    if team is None:
        raise TEAM_NOT_FOUND

    try:
        await User.update_team_id_by_uid(conn=conn, uid=user_id, team_id=team_uid)
    except PostgresError as e:
        if "TEAM_MEMBER_LIMIT_EXCEEDED" in str(e):
            raise TEAM_IS_FULL
        raise

    return team.to_model(TeamRead)


@router.get("/members")
async def get_team_members(
    conn: ConnDepends,
    user_id: UserIdDepends
) -> list[UserRead]:
    team_uid = await User.get_team_id_by_uid(conn=conn, uid=user_id)

    if team_uid is None:
        raise TEAM_NOT_FOUND

    return await User.get_users_by_team_id(
        conn=conn,
        team_id=team_uid,
        model_cls=UserRead
    )
