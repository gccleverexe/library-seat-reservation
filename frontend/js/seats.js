const { createApp } = Vue;

createApp({
    data() {
        return {
            seats: [],
            loading: false,
            error: '',
            filters: { floor: '', area: '', time_start: '', time_end: '' },
            showModal: false,
            selectedSeat: null,
            reserveForm: { start_time: '', end_time: '' },
            reserveError: '',
            reserveSuccess: '',
            reserveLoading: false,
        };
    },
    mounted() {
        if (!localStorage.getItem('access_token')) {
            window.location.href = '/pages/login.html';
            return;
        }
        this.loadSeats();
    },
    methods: {
        async loadSeats() {
            this.loading = true;
            this.error = '';
            try {
                const params = {};
                if (this.filters.floor) params.floor = parseInt(this.filters.floor);
                if (this.filters.area) params.area = this.filters.area;
                if (this.filters.time_start) params.time_start = this.filters.time_start;
                if (this.filters.time_end) params.time_end = this.filters.time_end;
                const res = await seatsAPI.list(params);
                this.seats = res.data || [];
            } catch (e) {
                this.error = e.message;
            } finally {
                this.loading = false;
            }
        },
        statusLabel(status) {
            const map = {
                available: '空闲',
                reserved: '已预约',
                occupied: '使用中',
                unavailable: '不可用',
            };
            return map[status] || status;
        },
        openReserve(seat) {
            this.selectedSeat = seat;
            this.reserveForm = { start_time: '', end_time: '' };
            this.reserveError = '';
            this.reserveSuccess = '';
            this.showModal = true;
        },
        async submitReservation() {
            this.reserveError = '';
            this.reserveSuccess = '';
            if (!this.reserveForm.start_time || !this.reserveForm.end_time) {
                this.reserveError = '请填写开始时间和结束时间';
                return;
            }
            this.reserveLoading = true;
            try {
                await reservationsAPI.create({
                    seat_id: this.selectedSeat.id,
                    start_time: this.reserveForm.start_time,
                    end_time: this.reserveForm.end_time,
                });
                this.reserveSuccess = '预约成功！';
                setTimeout(() => {
                    this.showModal = false;
                    this.loadSeats();
                }, 1500);
            } catch (e) {
                this.reserveError = e.message;
            } finally {
                this.reserveLoading = false;
            }
        },
        logout() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_info');
            window.location.href = '/pages/login.html';
        },
    },
}).mount('#app');
