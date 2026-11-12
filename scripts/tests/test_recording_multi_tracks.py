"""Verify multiple recording track lists and their independent controllers."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_content_authoring import Document, ROOT


class MultipleTrackLists(unittest.TestCase):
    def test_recording_callouts_attach_tracks_to_each_playlist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copy(ROOT / 'hugo.toml', root / 'hugo.toml')
            shutil.copytree(ROOT / 'content/Site Text', root / 'content/Site Text')
            (root / 'content/recordings').mkdir()
            (root / 'content/recordings/series.md').write_text('''---
title: Series
slug: series
youtube: https://www.youtube.com/playlist?list=PLone
tracks: ["First · 1:00"]
---
## Volume 2

> [!recording] [Volume 2](https://www.youtube.com/playlist?list=PLtwo)
>
> - Suite: I. Opening · 2:00 · Plain Composer
> - Suite: II. Closing · 3:00 · Plain Composer

## Volume 3

> [!recording] [Volume 3](https://www.youtube.com/playlist?list=PLthree)
>
> - Song & Dance · 4:00 · Other Composer
''')
            result = subprocess.run(
                ['hugo', '--source', str(root), '--layoutDir', str(ROOT / 'layouts')],
                text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            source = (root / 'public/recordings/series/index.html').read_text()
            doc = Document(source)
            self.assertEqual(len(doc.matching('div', 'player')), 3)
            self.assertEqual(len(doc.matching('section', 'tracks')), 3)
            self.assertEqual([a['data-i'] for a in doc.matching('button', 'track')],
                             ['0', '0', '1', '0'])
            frames = [a for tag, a in doc.tags if tag == 'iframe']
            self.assertEqual(len(frames), 3)
            for frame in frames:
                self.assertIn('enablejsapi=1', frame['src'])
            self.assertIn('Plain Composer', source)
            self.assertIn('Song &amp; Dance', source)
            self.assertNotIn('Song &amp;amp; Dance', source)

    def test_javascript_pairs_players_and_initializes_only_once(self):
        script = r'''
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync(process.argv[1], 'utf8');
function run(preloaded) {
  const mounts = [], scripts = [];
  const groups = [2,3,1].map((count, group) => {
    const rows = Array.from({length:count},(_,i)=>({
      attrs:{}, classList:{toggle(){}},
      setAttribute(k,v){this.attrs[k]=v;}, removeAttribute(k){delete this.attrs[k];},
      getAttribute(k){return k==='data-i'?String(i):this.attrs[k];},
      closest(){return this;}
    }));
    const frame={group};
    const list={handlers:[],querySelectorAll(){return rows;},
      addEventListener(type, fn){this.handlers.push(fn);},
      closest(){return wrapper;}};
    const wrapper={querySelector(s){return s==='[data-tracks]'?list:frame;}};
    return {rows,list,frame,wrapper};
  });
  const YT={PlayerState:{PLAYING:1,BUFFERING:3},Player:function(frame,opts){
    this.calls=[];this.index=0;this.playVideoAt=i=>this.calls.push(i);
    this.getPlaylistIndex=()=>this.index;this.opts=opts;this.frame=frame;
    mounts.push(this);
  }};
  const window={};
  const document={
    querySelectorAll(s){return s==='[data-tracks]'?groups.map(g=>g.list):groups.map(g=>g.wrapper);},
    querySelector(s){
      if(s==='[data-tracks]')return groups[0].list;
      if(s.includes('iframe_api'))return scripts[0]||null;
      return groups[0].frame;
    },
    createElement(){return {};},head:{appendChild(s){scripts.push(s);}}
  };
  const context=vm.createContext({window,document,YT});
  if(preloaded)window.YT=YT;
  vm.runInContext(code,context);
  vm.runInContext(code,context);
  groups[1].list.handlers.forEach(fn=>fn({target:groups[1].rows[1]}));
  if(!preloaded){window.YT=YT;window.onYouTubeIframeAPIReady();}
  assert.equal(mounts.length,3);
  mounts.forEach(p=>p.opts.events.onReady());
  assert.equal(groups[1].rows[1].attrs['aria-current'],'true');
  assert.deepEqual(mounts[1].calls,[1]);
  assert.equal(mounts[0].calls.length,0);
  assert.equal(mounts[2].calls.length,0);
  groups[0].list.handlers.forEach(fn=>fn({target:groups[0].rows[0]}));
  assert.deepEqual(mounts[0].calls,[0]);
  assert.equal(groups[1].rows[1].attrs['aria-current'],'true');
  mounts[1].index=2;mounts[1].opts.events.onStateChange({data:1});
  assert.equal(groups[1].rows[2].attrs['aria-current'],'true');
  assert.equal(groups[1].rows[1].attrs['aria-current'],undefined);
  assert.equal(groups[0].rows[0].attrs['aria-current'],'true');
  groups.forEach(g=>assert.equal(g.list.handlers.length,1));
  assert.equal(scripts.length,preloaded?0:1);
}
run(false);run(true);
'''
        result = subprocess.run(['node', '-e', script, str(ROOT / 'static/js/tracks.js')],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
