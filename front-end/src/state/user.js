import { reactive } from 'vue'

export const store = reactive({ 
    user: null,
    is_admin: false
})

export function forgetUser(instance) {
    store.user = null;
    store.is_admin = null;
    instance.$cookies.remove("username");
    instance.$cookies.remove("is_admin");
}