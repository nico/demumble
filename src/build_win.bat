RD /S /Q cmake-build
mkdir cmake-build 
cd cmake-build
cmake ..\
cmake --build . --config Release
copy Release\demumble_shared.dll ..\..\demumble\demumble_shared.dll
cd ..\
