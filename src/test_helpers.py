from auth import auth_register

def register_n_users(num_users):
    """
    Usage

    >>> single = register_n_users(1)
    >>> usera, userb = register_n_users(2)
    >>> usera, userb, userc = register_n_users(3)
    """
    assert isinstance(num_users, int)

    users = []
    for i in range(num_users):
        users.append(
            auth_register(f"email{i}@gmail.com", f"passwordthatislongenough{i}", f"first{i}", f"last{i}")
        )

    if len(users) == 1:
        return users[0]

    # try to make the job of autocompletion engines easier
    assert len(users) == num_users

    return users
