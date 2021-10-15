db.createUser({
    user: "mongo_user",
    pwd: "password",
    roles: [
        {
            role: "readWrite",
            db: "ymal"
        }
    ]
});

