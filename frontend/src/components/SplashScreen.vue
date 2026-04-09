<template>
  <div class="w-full h-full bg-base-200">
    <transition name="fade">
      <div id="splash" aria-hidden="true" class="bg-background/95 flex items-center justify-center">
        <svg
          aria-label="logo"
          class="logo"
          role="img"
          viewBox="0 0 512 512"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
        >
          <defs>
            <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stop-color="#ffffff" stop-opacity="0.1" />
              <stop offset="50%" stop-color="#a3a0a0" stop-opacity="0.25" />
              <stop offset="100%" stop-color="#ffffff" stop-opacity="0.1" />
              <animateTransform
                attributeName="gradientTransform"
                type="translate"
                dur="2s"
                repeatCount="indefinite"
                values="-1 0; 1 0"
                keyTimes="0; 1"
                calcMode="spline"
                keySplines="0.32 0 0.68 1"
              />
            </linearGradient>
          </defs>
          <path
            d="M206.4 300.8c1.6 10.4 4.8 18.4 8.8 24c8 9.6 21.6 14.4 41.6 14.4c12 0 20.8-1.6 28.8-4c13.6-4.8 20.8-13.6 20.8-27.2c0-8-3.2-13.6-10.4-17.6c-6.4-4-17.6-8-32-11.2l-24.8-5.6c-24.8-5.6-41.6-11.2-51.2-17.6c-16-10.4-23.2-27.2-23.2-50.4c0-20.8 8-38.4 23.2-52c15.2-13.6 37.6-20.8 67.2-20.8c24.8 0 45.6 6.4 63.2 19.2c17.6 12.8 26.4 32 27.2 56.8h-46.4c-.8-13.6-7.2-24-18.4-29.6c-8-4-17.6-5.6-28.8-5.6c-12.8 0-23.2 2.4-30.4 7.2s-11.2 12-11.2 20.8c0 8 4 14.4 11.2 18.4c4.8 2.4 15.2 5.6 31.2 9.6l40.8 9.6c17.6 4 31.2 9.6 40 16.8c13.6 11.2 20.8 26.4 20.8 47.2c0 21.6-8 39.2-24.8 52.8c-16 14.4-39.2 20.8-69.6 20.8c-30.4 0-54.4-7.2-72-20.8c-19.2-12-28-31.2-28-55.2h46.4"
            fill="url(#shine)"
          />
        </svg>
      </div>
    </transition>
  </div>
</template>

<style scoped>
#splash {
  position: fixed;
  inset: 0;
  z-index: 9999;
}

.logo {
  width: 256px;
  height: 256px;
  display: block;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.35s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-to,
.fade-leave-from {
  opacity: 1;
}
</style>
