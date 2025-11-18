from app.database.repositories.team import TeamRepo
from app.database.repositories.user import UserRepo
from app.exceptions import ModelExistException, NotFoundException
from app.schemas.team import TeamCreate, TeamMember, TeamResponse


class TeamService:
    def __init__(self, team_repo: TeamRepo, user_repo: UserRepo) -> None:
        self.team_repo = team_repo
        self.user_repo = user_repo

    async def add_team(self, team_data: TeamCreate) -> TeamResponse:
        """
        Создает команду с участниками.

        :raises ModelExistException: Команда уже существует.
        """
        team_exists = await self.team_repo.exists(team_data.team_name)
        if team_exists:
            raise ModelExistException()

        team = await self.team_repo.create(team_data.team_name)

        created_members = []
        for member in team_data.members:
            user = await self.user_repo.create_or_update(
                user_id=member.user_id,
                username=member.username,
                team_name=team_data.team_name,
                is_active=member.is_active,
            )
            created_members.append(
                TeamMember(
                    user_id=user.user_id,
                    username=user.username,
                    is_active=user.is_active,
                )
            )

        return TeamResponse(
            team_name=team.team_name,
            members=created_members,
        )

    async def get_team(self, team_name: str) -> TeamResponse:
        """
        Возвращает команду по имени с ее участниками.

        :raises NotFoundException: Команда не найдена.
        """
        team = await self.team_repo.get_by_name(team_name)

        if not team:
            raise NotFoundException()

        members = [
            TeamMember(
                user_id=member.user_id,
                username=member.username,
                is_active=member.is_active,
            )
            for member in team.members
        ]

        return TeamResponse(
            team_name=team.team_name,
            members=members,
        )
