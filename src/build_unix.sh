rm -rf cmake-build
mkdir -p cmake-build && cd cmake-build
cmake ../
cmake --build . --config Release

# copy lib from build to python script dir
cp libdemumble_shared.so ../../demumble/libdemumble_shared.so
cd ../
