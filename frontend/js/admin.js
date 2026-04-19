const { createApp } = Vue;

createApp({
    data() {
        return {
            activeTab: 'seats',
            mainTabs: [
                { key: 'seats',        label: '座位管理' },
                { key: 'reservations', label: '预约管理' },
                { key: 'violations',   label: '违规记录' },
                { key: 'dashboard',    label: '统计看板' },
            ],
            globalError: '',

            // 座位管理
            seats: [],
            seatsLoading: false,
            showSeatModal: false,
            editingSeat: null,
            seatForm: { seat_number: '', floor: 1, area: '', description: '' },
            seatError: '',
            seatLoading: false,

            // 预约管理
            reservations: [],
            resFilters: { date: '', status: '' },

            // 违规记录
            violations: [],
            violationStudentId: '',
            violationError: '',
            violationSuccess: '',

            // 统计看板
            summary: null,
            hotSeats: [],
            hourlyData: [],
            dashboardLoading: false,
        };
    },

    computed: {
        maxHourly() {
            return Math.max(...this.hourlyData.map(h => h.count), 1);
        }
    },

    mounted() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            window.location.href = '/pages/login.html';
            return;
        }
        const user = JSON.parse(localStorage.getItem('user_info') || '{}');
        if (user.role !== 'admin') {
            window.location.href = '/pages/seats.html';
            return;
        }
        this.loadSeats();
    },

    methods: {
        switchTab(tab) {
            this.activeTab = tab;
            this.globalError = '';
            if (tab === 'seats')        this.loadSeats();
            else if (tab === 'reservations') this.loadReservations();
            else if (tab === 'dashboard')    this.loadDashboard();
        },

        // ── 座位管理 ──────────────────────────────────────────────
        async loadSeats() {
            this.seatsLoading = true;
            try {
                const res = await seatsAPI.list({});
                this.seats = res.data || [];
            } catch (e) {
                this.globalError = e.message;
            } finally {
                this.seatsLoading = false;
            }
        },

        openSeatModal(seat = null) {
            this.editingSeat = seat;
            this.seatError = '';
            this.seatForm = seat
                ? { seat_number: seat.seat_number, floor: seat.floor, area: seat.area, description: seat.description || '' }
                : { seat_number: '', floor: 1, area: '', description: '' };
            this.showSeatModal = true;
        },

        async saveSeat() {
            this.seatError = '';
            this.seatLoading = true;
            try {
                if (this.editingSeat) {
                    await adminAPI.updateSeat(this.editingSeat.id, this.seatForm);
                } else {
                    await adminAPI.createSeat(this.seatForm);
                }
                this.showSeatModal = false;
                await this.loadSeats();
            } catch (e) {
                this.seatError = e.message;
            } finally {
                this.seatLoading = false;
            }
        },

        async deleteSeat(id) {
            if (!confirm('确认删除此座位？')) return;
            try {
                await adminAPI.deleteSeat(id);
                await this.loadSeats();
            } catch (e) {
                this.globalError = e.message;
            }
        },

        async toggleSeatStatus(seat) {
            const newStatus = seat.status === 'unavailable' ? 'available' : 'unavailable';
            try {
                await adminAPI.setSeatStatus(seat.id, { status: newStatus });
                await this.loadSeats();
            } catch (e) {
                this.globalError = e.message;
            }
        },

        seatStatusLabel(s) {
            const m = { available: '空闲', reserved: '已预约', occupied: '使用中', unavailable: '不可用' };
            return m[s] || s;
        },

        // ── 预约管理 ──────────────────────────────────────────────
        async loadReservations() {
            try {
                const params = {};
                if (this.resFilters.date)   params.date   = this.resFilters.date;
                if (this.resFilters.status) params.status = this.resFilters.status;
                const res = await adminAPI.listReservations(params);
                this.reservations = res.data?.items || res.data || [];
            } catch (e) {
                this.globalError = e.message;
            }
        },

        async cancelReservation(id) {
            if (!confirm('确认强制取消此预约？')) return;
            try {
                await adminAPI.cancelReservation(id);
                await this.loadReservations();
            } catch (e) {
                this.globalError = e.message;
            }
        },

        resStatusLabel(s) {
            const m = {
                active:            '待签到',
                checked_in:        '使用中',
                completed:         '已完成',
                cancelled:         '已取消',
                timeout_cancelled: '超时取消',
            };
            return m[s] || s;
        },

        // ── 违规记录 ──────────────────────────────────────────────
        async searchViolations() {
            this.violationError = '';
            this.violationSuccess = '';
            if (!this.violationStudentId) {
                this.violationError = '请输入用户ID';
                return;
            }
            try {
                const res = await adminAPI.getViolations(this.violationStudentId);
                this.violations = res.data || [];
            } catch (e) {
                this.violationError = e.message;
            }
        },

        async liftRestriction() {
            if (!confirm('确认解除该用户的预约限制？')) return;
            this.violationError = '';
            this.violationSuccess = '';
            try {
                await adminAPI.liftRestriction(this.violationStudentId);
                this.violationSuccess = '限制已解除';
                setTimeout(() => { this.violationSuccess = ''; }, 3000);
            } catch (e) {
                this.violationError = e.message;
            }
        },

        // ── 统计看板 ──────────────────────────────────────────────
        async loadDashboard() {
            this.dashboardLoading = true;
            try {
                const [sumRes, hotRes, hourRes] = await Promise.all([
                    adminAPI.getSummary({}),
                    adminAPI.getHotSeats(),
                    adminAPI.getHourly(),
                ]);
                this.summary     = sumRes.data;
                this.hotSeats    = hotRes.data  || [];
                this.hourlyData  = hourRes.data || [];
            } catch (e) {
                this.globalError = e.message;
            } finally {
                this.dashboardLoading = false;
            }
        },

        pct(val) {
            if (val == null) return '-';
            return (val * 100).toFixed(1) + '%';
        },

        formatTime(t) {
            return t ? new Date(t).toLocaleString('zh-CN') : '-';
        },

        logout() {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_info');
            window.location.href = '/pages/login.html';
        },
    }
}).mount('#app');
