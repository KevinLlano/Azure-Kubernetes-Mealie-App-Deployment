from fastapi import HTTPException, status
from pydantic import UUID4

from mealie.core.security import hash_password
from mealie.core.security.providers.credentials_provider import CredentialsProvider
from mealie.db.models.users.users import AuthMethod
from mealie.routes._base import BaseUserController, controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.routes.users._helpers import assert_user_change_allowed
from mealie.schema.response import ErrorResponse, SuccessResponse
from mealie.schema.user import ChangePassword, UserBase, UserOut
from mealie.schema.user.user import UserRatings, UserRatingSummary

user_router = UserAPIRouter(prefix="/users", tags=["Users: CRUD"])


@controller(user_router)
class UserController(BaseUserController):
    @user_router.get("/self", response_model=UserOut)
    def get_logged_in_user(self):
        return self.user

    @user_router.get("/self/ratings", response_model=UserRatings[UserRatingSummary])
    def get_logged_in_user_ratings(self):
        return UserRatings(ratings=self.repos.user_ratings.get_by_user(self.user.id))

    @user_router.get("/self/ratings/{recipe_id}", response_model=UserRatingSummary)
    def get_logged_in_user_rating_for_recipe(self, recipe_id: UUID4):
        user_rating = self.repos.user_ratings.get_by_user_and_recipe(self.user.id, recipe_id)
        if user_rating:
            return user_rating
        else:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                ErrorResponse.respond("User has not rated this recipe"),
            )

    @user_router.get("/self/favorites", response_model=UserRatings[UserRatingSummary])
    def get_logged_in_user_favorites(self):
        return UserRatings(ratings=self.repos.user_ratings.get_by_user(self.user.id, favorites_only=True))

    @user_router.put("/password")
    def update_password(self, password_change: ChangePassword):
        """Resets the User Password"""
        if self.user.password == "LDAP" or self.user.auth_method == AuthMethod.LDAP:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorResponse.respond(self.t("user.ldap-update-password-unavailable"))
            )
        if not CredentialsProvider.verify_password(password_change.current_password, self.user.password):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, ErrorResponse.respond(self.t("user.invalid-current-password"))
            )

        self.user.password = hash_password(password_change.new_password)
        try:
            self.repos.users.update_password(self.user.id, self.user.password)
        except Exception as e:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorResponse.respond("Failed to update password"),
            ) from e

        return SuccessResponse.respond(self.t("user.password-updated"))

    @user_router.put("/{item_id}")
    def update_user(self, item_id: UUID4, new_data: UserBase):
        assert_user_change_allowed(item_id, self.user, new_data)

        try:
            self.repos.users.update(item_id, new_data.model_dump())
        except Exception as e:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                ErrorResponse.respond("Failed to update user"),
            ) from e

        return SuccessResponse.respond(self.t("user.user-updated"))
