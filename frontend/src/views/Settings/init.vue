<script setup>
import { useI18n } from "vue-i18n"
import { supported } from "@/locales"

const { locale, t } = useI18n()

function setLang(l) {
  if (l === locale.value) return
  locale.value = l
  document.cookie = `lang=${l};path=/;max-age=31536000`
}
</script>


<template>
    <div class="flex flex-col space-y-2 mt-8 mb-12">
        <h1 class="text-4xl font-bold">
            {{ $t("views.settings.header") }}
        </h1>
        <p class="text-gray-400 text-base">{{ $t("views.settings.hint") }}</p>
    </div>
    <div class="flex flex-col w-full max-w- mx-auto p-2 mb-8 gap-6">
        <ul class="list bg-base-100 rounded-box shadow-md w-full relative">
            <li>
                <span class="list-row items-center flex w-full">
                    <i class="ri-moon-line text-3xl"></i>
                    <div class="flex-1">{{ $t("views.settings.general.theme") }}</div>
                    <input type="checkbox" checked="checked" class="toggle toggle-accent m-1" />
                </span>
            </li>
            <li>
                <span class="list-row items-center flex w-full">
                    <i class="ri-translate text-3xl"></i>
                    <div class="flex-1">{{ $t("views.settings.general.language") }}</div>
                    <div class="dropdown dropdown-end">
                        <div class="dropdown dropdown-end">
                            <div tabindex="0" role="button" class="btn m-1 flex items-center gap-2">
                                <span>{{ t(`lang_select.${locale}`) }}</span>
                                <i class="ri-arrow-down-s-line leading-none"></i>
                            </div>
                            <ul tabindex="0"
                                class="dropdown-content menu bg-gray-600 rounded-box z-1 w-max min-w-[6rem] p-2 shadow-xl">
                                <li v-for="l in supported" :key="l">
                                    <button class="w-full text-left"
                                        :class="l === locale ? 'bg-accent text-gray-900 pointer-events-none' : ''"
                                        @click="setLang(l)">
                                        {{ t(`lang_select.${l}`) }}
                                    </button>
                                </li>
                            </ul>
                        </div>
                    </div>
                </span>
            </li>
        </ul>
        <ul class="list bg-base-100 rounded-box shadow-md w-full relative">
            <li>
                <a @click="$router.push('/settings/about')" class="list-row items-center flex w-full">
                    <i class="ri-information-2-line text-3xl"></i>
                    <div class="flex-1">{{ $t("views.settings.additional.about") }}</div>
                    <i class="ri-arrow-right-s-line text-2xl m-1 leading-none"></i>
                </a>
            </li>
        </ul>

    </div>
</template>