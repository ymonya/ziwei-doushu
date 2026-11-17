#!/usr/bin/env bash
# 紫微斗数 Android APK 构建脚本（Linux / 无 Gradle，纯 aapt2 + javac + d8 + apksigner）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SDK="${ANDROID_SDK:-/opt/android-sdk}"
BT="$SDK/build-tools/35.0.1"
AJ="$SDK/platforms/android-35/android.jar"
WEB_DIR="$(cd "$ROOT/.." && pwd)"
OUT="${APK_OUT:-$WEB_DIR/ziwei-doushu-v1.0.apk}"

# 签名口令只从环境变量读取，绝不写入仓库。
# 首次构建会用它生成 ziwei.jks；已有密钥时它必须与生成时的口令一致。
if [ -z "${KS_PASS:-}" ]; then
  echo "缺少 KS_PASS：请先执行 export KS_PASS='你的签名口令' 再运行本脚本" >&2
  exit 1
fi

cd "$ROOT"
echo "=== 0. 校验工具链 ==="
for f in "$BT/aapt2" "$BT/d8" "$BT/zipalign" "$BT/apksigner" "$AJ"; do
  [ -e "$f" ] || { echo "缺少: $f"; exit 1; }
done
echo "  SDK: $SDK"

echo "=== 1. 生成竖屏版页面与图标 ==="
python3.11 build_mobile.py
python3.11 make_icon.py
mkdir -p assets/data/years
cp -f "$WEB_DIR"/data/years/*.jsonl.zst assets/data/years/
echo "  assets: $(find assets -type f | wc -l) 个文件, $(du -sh assets | cut -f1)"

echo "=== 2. 生成签名密钥（仅首次） ==="
if [ ! -f ziwei.jks ]; then
  keytool -genkeypair -v -keystore ziwei.jks -storetype PKCS12 \
    -alias ziwei -keyalg RSA -keysize 2048 -validity 10000 \
    -storepass "$KS_PASS" -keypass "$KS_PASS" \
    -dname "CN=Ziwei Dou Shu, OU=Local Build, O=ZiweiApp, L=CN, ST=CN, C=CN" \
    > build_key.log 2>&1
  echo "  已创建 ziwei.jks"
else
  echo "  复用已有 ziwei.jks"
fi

echo "=== 3. 清理并编译资源 ==="
rm -rf build out && mkdir -p build/classes build/dex out
"$BT/aapt2" compile --dir res -o build/res.zip
"$BT/aapt2" link -o build/base.apk -I "$AJ" \
  --manifest AndroidManifest.xml -R build/res.zip -A assets -0 zst \
  --auto-add-overlay --min-sdk-version 24 --target-sdk-version 35
echo "  base.apk: $(stat -c%s build/base.apk) bytes"

echo "=== 4. 编译 Java 并转 dex ==="
if ! javac -source 8 -target 8 -cp "$AJ" -d build/classes \
      src/com/ziwei/app/MainActivity.java > build/javac.log 2>&1; then
  echo "  javac -source 8 失败，改用 --release 8"
  javac --release 8 -cp "$AJ" -d build/classes src/com/ziwei/app/MainActivity.java
fi
echo "  class 数: $(find build/classes -name '*.class' | wc -l)"
"$BT/d8" --lib "$AJ" --min-api 24 --output build/dex \
  $(find build/classes -name '*.class') 2>&1 | tail -5
[ -f build/dex/classes.dex ] || { echo "classes.dex 未生成"; exit 1; }

echo "=== 5. 并入 dex ==="
cp build/base.apk build/unsigned.apk
(cd build && zip -q -j unsigned.apk dex/classes.dex)
unzip -l build/unsigned.apk | grep -E 'classes.dex|assets/index.html|AndroidManifest.xml' | head -5

echo "=== 6. 对齐并签名 ==="
"$BT/zipalign" -f 4 build/unsigned.apk build/aligned.apk
"$BT/apksigner" sign \
  --ks ziwei.jks --ks-pass "pass:$KS_PASS" --key-pass "pass:$KS_PASS" \
  --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
  --out out/app-release.apk build/aligned.apk
"$BT/apksigner" verify --verbose out/app-release.apk | head -12

echo "=== 7. 输出成品 ==="
cp out/app-release.apk "$OUT"
echo "  $OUT  $(stat -c%s "$OUT") bytes ($(du -h "$OUT" | cut -f1))"
"$BT/aapt2" dump badging "$OUT" | head -8
echo "DONE"
