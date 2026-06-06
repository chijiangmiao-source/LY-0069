from ninja import Schema


class LoginSchema(Schema):
    username: str
    password: str


class LoginResponseSchema(Schema):
    token: str
    token_type: str = 'Bearer'
    expires_in: int


class UserInfoSchema(Schema):
    id: int
    username: str
    email: str
    role: str
    first_name: str
    last_name: str
