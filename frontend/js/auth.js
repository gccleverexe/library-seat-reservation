const { createApp } = Vue;

createApp({
    data() {
        return {
            tab: 'login',
            loading: false,
            loginForm: { campus_id: '', password: '' },
            regForm: { campus_id: '', name: '', password: '' },
            loginError: '',
            regError: '',
            regSuccess: '',
        };
    },
    mounted() {
        // Redirect if already logged in
        if (localStorage.getItem('access_token')) {
            window.location.href = '/pages/seats.html';
        }
    },
    methods: {
        async doLogin() {
            this.loginError = '';
            this.loading = true;
            try {
                const res = await authAPI.login(this.loginForm);
                const token = res.data.access_token;
                localStorage.setItem('access_token', token);
                // Get user info
                const userRes = await authAPI.me();
                localStorage.setItem('user_info', JSON.stringify(userRes.data));
                // Redirect based on role
                if (userRes.data.role === 'admin') {
                    window.location.href = '/pages/admin.html';
                } else {
                    window.location.href = '/pages/seats.html';
                }
            } catch (e) {
                this.loginError = e.message;
            } finally {
                this.loading = false;
            }
        },
        async doRegister() {
            this.regError = '';
            this.regSuccess = '';
            this.loading = true;
            try {
                await authAPI.register(this.regForm);
                this.regSuccess = '注册成功！请登录';
                this.tab = 'login';
                this.loginForm.campus_id = this.regForm.campus_id;
            } catch (e) {
                this.regError = e.message;
            } finally {
                this.loading = false;
            }
        },
    }
}).mount('#app');
