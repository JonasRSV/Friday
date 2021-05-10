#!/bin/bash

# This makes takes the 'build' directory and creates a 'release' directory
# that is a servable Friday GUI

npm run build

rm -rf release

mkdir -p release/static

cp public/index.html release
cp public/favicon.png release/static
cp public/global.css release/static
cp public/build/* release/static
cp -r public/assets/ release/static/assets

rm release/static/bundle.js.map

# Update files paths

sed -i "s%/global.css%static/global.css%g" release/index.html
sed -i "s%/build/bundle.css%static/bundle.css%g" release/index.html
sed -i "s%/build/bundle.js%static/bundle.js%g" release/index.html
sed -i "s%/favicon.png%static/favicon.png%g" release/index.html
sed -i "s%/assets/icons/%/static/assets/icons/%g" release/static/bundle.css
sed -i "s%/assets/icons/%/static/assets/icons/%g" release/static/global.css
sed -i "s%/assets/icons/%/static/assets/icons/%g" release/static/bundle.js


