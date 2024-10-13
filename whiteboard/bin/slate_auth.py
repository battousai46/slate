from starlette.authentication import AuthenticationBackend, SimpleUser
from helper.logging_slate import get_logger
from jwt import decode, get_unverified_header
logger = get_logger(__name__)

class User(SimpleUser):
    def __init__(self, user_name, roles):
        self.username = user_name
        super().__init__(username=user_name)
        self.roles = roles.split("|") if roles else []


class CustomSlateAuth(AuthenticationBackend):

    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            logger.warn("no authorization header")
            return

        auth = request.headers["Authorization"]
        if  not auth.startswith("Bearer "):
            logger.warn("not a bearer token")
            return
        try:
            scheme, token = auth.split(" ")
            alg = get_unverified_header(token)["alg"]

            decoded_token = decode(token,algorithms=alg,key="super_secret")
            roles = decoded_token.get("roles")

        except Exception as ex:
            logger.warn(f"failed to decode token {str(ex)}")
            return

        user = User(
            user_name=decoded_token.get("sub"),
            roles=roles,
        )

        return auth, user

