
# project URLS Documentation
http://127.0.0.1:8000/

######################## Authentication ###########################

POST      /api/register/user/                        →for register
POST     /api/login/user/                            →for login
POST    /api/logout/user/                            →for logout
POST   /api/change-password/user/                    →for change password
POST  /api/reset-password/user/                      →for reset password


#########################User CRUD ###############################

GET                  /api/users/                     →GET user
GET BY ID            /api/users/<id>/                →GET BY ID user
POST                 /api/users/                     →POST user
PATCH                /api/users/<id>/                →Update user
DELETE              /api/users/<id>/                 →Delete user


############################## DATA APP #########################

GET                /api/app-data/                   →GET APP DATA
GET BY ID          /api/app-data/<id>/              →GET BY ID APP DATA
POST               /api/app-data/                   →POST APP DATA
PATCH              /api/app-data/<id>/              →Update APP DATA
DELETE             /api/app-data/<id>/              →DELETE APP DATA


###################### DOMAIN #####################################

GET               /api/users/total-history/          →GET ALL REGISTER USER
GET               /api/users/active/                 →GET ACTIVE USER 
GET               /api/users/deactive/               →GET DEACTIVE USER 
GET               /api/cron/check-domains/           →GET CRON DOMAIN 