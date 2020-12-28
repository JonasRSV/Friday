#!/bin/bash

# This makes takes the 'build' directory and creates a 'release' directory
# that is a servable Friday GUI

npm run build

mkdir -p release/static

cp public/index.html release
cp public/favicon.png release/static
cp public/global.css release/static
cp public/build/* release/static

# Update files paths

sed -i "s%/global.css%static/global.css%g" release/index.html
sed -i "s%/build/bundle.css%static/bundle.css%g" release/index.html
sed -i "s%/build/bundle.js%static/bundle.js%g" release/index.html
sed -i "s%/favicon.png%static/favicon.png%g" release/index.html

