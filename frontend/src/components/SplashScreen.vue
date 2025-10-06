<script setup lang="js">
</script>

<template>
  <div id="splash" aria-hidden="true">
    <div style="text-align: center">
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
            <stop offset="50%" stop-color="#a3a0a0" stop-opacity="0.2" />
            <stop offset="100%" stop-color="#7d7c7c" stop-opacity="0.1" />
            <animateTransform
              attributeName="gradientTransform"
              type="translate"
              from="-1 0"
              to="1 0"
              dur="2.2s"
              repeatCount="indefinite"
            />
          </linearGradient>
        </defs>
        <path
          d="M206.4 300.8c1.6 10.4 4.8 18.4 8.8 24c8 9.6 21.6 14.4 41.6 14.4c12 0 20.8-1.6 28.8-4c13.6-4.8 20.8-13.6 20.8-27.2c0-8-3.2-13.6-10.4-17.6c-6.4-4-17.6-8-32-11.2l-24.8-5.6c-24.8-5.6-41.6-11.2-51.2-17.6c-16-10.4-23.2-27.2-23.2-50.4c0-20.8 8-38.4 23.2-52c15.2-13.6 37.6-20.8 67.2-20.8c24.8 0 45.6 6.4 63.2 19.2c17.6 12.8 26.4 32 27.2 56.8h-46.4c-.8-13.6-7.2-24-18.4-29.6c-8-4-17.6-5.6-28.8-5.6c-12.8 0-23.2 2.4-30.4 7.2s-11.2 12-11.2 20.8c0 8 4 14.4 11.2 18.4c4.8 2.4 15.2 5.6 31.2 9.6l40.8 9.6c17.6 4 31.2 9.6 40 16.8c13.6 11.2 20.8 26.4 20.8 47.2c0 21.6-8 39.2-24.8 52.8c-16 14.4-39.2 20.8-69.6 20.8c-30.4 0-54.4-7.2-72-20.8c-19.2-12-28-31.2-28-55.2h46.4"
          fill="url(#shine)"
        />
      </svg>
    </div>
  </div>
</template>

<style scoped>
#splash {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  z-index: 9999;
  transition:
    opacity 350ms ease,
    visibility 350ms ease;
  opacity: 1;
  visibility: visible;
}

#splash.hidden {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
}

#splash .logo {
  width: 256px;
  height: 256px;
  display: block;
}
</style>
