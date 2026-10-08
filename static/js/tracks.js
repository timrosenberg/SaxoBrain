// Track list under a recording's YouTube playlist (layouts/_partials/recordings/tracks.html).
// Clicking a row plays that track in the embedded player; the playing track is highlighted.
// Uses YouTube's IFrame Player API on the existing iframe (its src carries enablejsapi=1).
(function () {
  var list = document.querySelector('[data-tracks]');
  var frame = document.querySelector('.video.has-tracks iframe');
  if (!list || !frame) return;
  var rows = Array.prototype.slice.call(list.querySelectorAll('button.track'));
  var player = null, ready = false, pending = null;

  function mark(i, playing) {
    rows.forEach(function (b, j) {
      var on = j === i;
      b.classList.toggle('current', on);
      b.classList.toggle('playing', on && playing);
      if (on) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current');
    });
  }

  list.addEventListener('click', function (e) {
    var b = e.target.closest('button.track');
    if (!b) return;
    var i = +b.getAttribute('data-i');
    mark(i, true);
    if (ready) player.playVideoAt(i); else pending = i;
  });

  var previous = window.onYouTubeIframeAPIReady;
  window.onYouTubeIframeAPIReady = function () {
    if (previous) previous();
    player = new YT.Player(frame, {
      events: {
        onReady: function () {
          ready = true;
          if (pending !== null) { player.playVideoAt(pending); pending = null; }
        },
        onStateChange: function (e) {
          var i = player.getPlaylistIndex();
          if (i >= 0) mark(i, e.data === YT.PlayerState.PLAYING || e.data === YT.PlayerState.BUFFERING);
        }
      }
    });
  };
  var s = document.createElement('script');
  s.src = 'https://www.youtube.com/iframe_api';
  document.head.appendChild(s);
})();
