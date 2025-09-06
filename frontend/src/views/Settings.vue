<template>
    <div class="flex flex-col space-y-2 mt-8 mb-12">
        <h1 class="text-4xl font-bold">
            Settings
        </h1>
        <p class="text-gray-400 text-base">Setup notifications and see other info</p>
    </div>
    <div class="flex flex-col w-full max-w- mx-auto p-2 mb-10">
        <ul class="list bg-base-100 rounded-box shadow-md w-full relative hower:bg-base-200">
            <li class="list-row items-center">
                <i class="ri-github-fill text-2xl"></i>
                <div>
                    <div>Authors</div>
                </div>
                <a class="btn btn-square btn-ghost" href="https://github.com/sht0rmx/MiniAppTemplate">
                    <i class="ri-arrow-right-s-line"></i>
                </a>
            </li>
        </ul>
    </div>
    <div class="text-center items-center text-sm text-gray-400 mt-5 space-y-2">
        made with ❤️ by @sht0rmx        
    </div>
    <div class="text-center items-center text-sm text-gray-400 mt-2 space-x-2">
        <div class="badge badge-sm" :class="badgeDb" @click="fetchStatus();">{{ status }}</div>
        <div class="badge badge-sm" :class="badgeAuth" @click="checkAuth();">{{ status_auth }}</div>       
    </div>
</template>

<script setup lang="js">
import { ref } from 'vue';
import pb from '@/pocketbase';

const badgeDb = ref('badge-outline badge-info');
const badgeAuth = ref('badge-outline badge-info');
const status = ref('Loading...');
const status_auth = ref('...')

async function checkAuth() {
    const ok = pb.authStore.isValid

    if (ok) {
        const user = pb.authStore.record
        const uname = user?.username || user?.email || "unknown"
        
        badgeAuth.value = "badge-success"
        status_auth.value = `auth as @${uname}`
    } else {
        badgeAuth.value = "badge-error"
        status_auth.value = "auth error"
    }
}

async function fetchStatus() {
  try {
    const result = await pb.health.check();
    if (result.code !== 200) {
      badgeDb.value = 'badge badge-error';
      status.value = 'api unavailable';
    } 
    else {
      badgeDb.value = 'badge badge-success';
      status.value = "api is healthy"
    }
  } catch (error) {
    console.error('Failed to fetch db status:', error);
    badgeDb.value = "badge-warning"
    status.value = 'db unavailable';
  }
}

fetchStatus();
checkAuth();
</script>