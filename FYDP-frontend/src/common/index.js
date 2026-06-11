const backendDomain = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8080'
    : 'https://trustmark-superuser-backend-dyf5cmd8g5hqa6ax.malaysiawest-01.azurewebsites.net';

const summaryApi={
    signUp:{
        url: `${backendDomain}/api/signup`,
        method: "post"
    },
    login:{
        url: `${backendDomain}/api/login`,
        method: "post"
    },
    currentUser:{
        url: `${backendDomain}/api/user-details`,
        method: "get"
    },
    userLogout:{
        url: `${backendDomain}/api/user-logout`,
        method: "get"
    }
    
}

export default summaryApi