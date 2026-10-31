/* Legacy-page redirect: sends old URLs (resume.html, vfx.html, ...) to the matching section of the one-page site. */
(function(){var s=document.currentScript,t=s&&s.getAttribute('data-to');if(t)location.replace(t+(location.search||''));})();
