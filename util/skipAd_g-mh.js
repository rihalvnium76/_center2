// ==UserScript==
// @name         G社漫画去跳转广告
// @namespace    http://tampermonkey.net/
// @version      0.0.1
// @description  在特定网站DOMContentLoaded后执行代码
// @author       null
// @match        https://m.g-mh.org/manga/*
// @run-at       document-start
// @grant        none
// ==/UserScript==

(function() {
  'use strict';
  const futureTime = Math.floor(Date.now()/1000 + 3600).toString();
  localStorage.setItem("showAds", futureTime);
  document.cookie = `showAds=${futureTime}; max-age=3600; path=/`;

  document.addEventListener('DOMContentLoaded', function() {
    document.querySelector("a#preChapterLink").classList.add("closeAd");
    document.querySelector("a#nextChapterLink").classList.add("closeAd");
  });
})();
