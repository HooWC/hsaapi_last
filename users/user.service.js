const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

const { secret } = require('../config.json');
const db = require('../_helpers/db');

module.exports = {
    authenticate,
    getAll,
    getById,
    create,
    update,
    delete: _delete
};

async function authenticate({ username, password }) {    
    try {
        // Get user from database
        const conn = await db.getConnection();
        if (!conn) {
            throw 'Database connection failed';
        }
        
        const result = await conn.request()
            .input('username', username)
            .query('SELECT Id, Username, Password FROM Users WHERE username = @username');
        
        // Validate username and password
        if (result.recordset.length === 0) {
            //throw 'Username or password is incorrect';
        }
        
        const user = result.recordset[0];
        
        // Check password
        if (!await bcrypt.compare(password, user.Password)) {
            //throw 'Username or password is incorrect';
        }
        
        // Authentication successful - generate JWT token
        const token = jwt.sign({ sub: user.Id }, secret, { expiresIn: '7d' });
        
        // Return user info and token
        return {
            user: {
                id: user.Id,
                username: user.Username
            },
            token
        };
    } catch (error) {
        //console.error("Authentication error:", error);
        //throw error;
    }
}

async function getAll() {
    const conn = await db.getConnection();
    const res = await conn.request().execute("api_getAllUsers");
   
    var user = new Array();
    
    for (var i = 0; i < res.recordset.length; i++) {
        var id = res.recordset[i].Id;
        var title = res.recordset[i].Title;
        var firstName = res.recordset[i].FirstName;
        var lastName = res.recordset[i].LastName;
        var email = res.recordset[i].Email;
        var username = res.recordset[i].Username;
        var role = res.recordset[i].Role;            

        user.push({'id': id, 'title': title, 'firstName': firstName, 
                    'lastName': lastName, 'email': email,
                    'username': username, 'role': role});
    }
    
    return user;
    //return await db.User.findAll();
}

async function getById(id) {    
    return await getUser(id);
}

async function create(params) {
    // validate
    const conn = await db.getConnection();
    const resChecking = await conn.request().input('input_parameter', params.username).
            query('SELECT id,username, password FROM Users WHERE username = @input_parameter');

    if (resChecking.recordset.length >= 1)
        throw 'Username "' + params.username + '" is already taken';

    // hash password
    if (params.password) {
        passwordHash = await bcrypt.hash(params.password, 10);
    } else {
        throw 'No password is provided';
    }

    // Set default role to 'User' if not provided
    const role = params.role || 'User';

    // Convert Title based on gender input
    let title = params.title;
    if (title && (title.toLowerCase() === 'male')) {
        title = 'Mr.';
    } else if (title && (title.toLowerCase() === 'female')) {
        title = 'Ms.';
    }

    // save user
    const res = await conn.request()
        .input("title", title)
        .input("firstName", params.firstName)
        .input("lastName", params.lastName)
        .input("email", params.email)
        .input("role", role)
        .input("username", params.username)
        .input("password", passwordHash)
        .execute("api_addUser");

    return res;
}

async function update(id, params) {
    const user = await getUser(id);

    // validate
    const usernameChanged = params.username && user.username !== params.username;
    // if (usernameChanged && await db.User.findOne({ where: { username: params.username } })) {
    //     throw 'Username "' + params.username + '" is already taken';
    // }

    const conn = await db.getConnection();
    const resChecking = await conn.request().input('input_parameter', params.username).
            query('SELECT id,username, password FROM Users WHERE username = @input_parameter');

    if (usernameChanged && resChecking.recordset.length >= 1)
        throw 'Username "' + params.username + '" is already taken';

    // hash password if it was entered
    var passwordHash = '';

    if (params.password) {
        passwordHash = await bcrypt.hash(params.password, 10);
    }

    // copy params to user and save
    const res = await conn.request()
        .input("id", id)
        .input("title", params.title == undefined ? '' : params.title)
        .input("firstName", params.firstName == undefined ? '' : params.firstName)
        .input("lastName", params.lastName == undefined ? '' : params.lastName)
        .input("email", params.email == undefined ? '' : params.email)
        .input("role", params.role == undefined ? '' : params.role)
        .input("username", params.username == undefined ? '' : params.username)
        .input("password", passwordHash)
        .execute("api_updateUser");

    return res;
    //Object.assign(user, params);
    //await user.save();

    //return omitHash(user.get());
}

async function _delete(id) {
    await getUser(id);

    const conn = await db.getConnection();
    const res = await conn.request()
        .input("id", id)
        .execute("api_deleteUserById");

    return res;    
    
    // await user.destroy();
}

// helper functions

async function getUser(id) {
    // const user = await db.User.findByPk(id);
    // if (!user) throw 'User not found';

    const conn = await db.getConnection();
    const res = await conn.request()
        .input("id", id)
        .execute("api_getUserById");

    if (res.recordset.length == 0) throw 'User not found';    

    var user = new Array();

    for (var i = 0; i < res.recordset.length; i++) {
        var id = res.recordset[i].Id;
        var title = res.recordset[i].Title;
        var firstName = res.recordset[i].FirstName;
        var lastName = res.recordset[i].LastName;
        var email = res.recordset[i].Email;
        var username = res.recordset[i].Username;
        var role = res.recordset[i].Role;            

        user.push({'id': id, 'title': title, 'firstName': firstName, 
                    'lastName': lastName, 'email': email,
                    'username': username, 'role': role});
    }
    
    return user;    
}
