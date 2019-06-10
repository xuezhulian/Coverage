scripts="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export | egrep '( BUILT_PRODUCTS_DIR)|(CURRENT_ARCH)|(OBJECT_FILE_DIR_normal)|(SRCROOT)|(OBJROOT)|(TARGET_DEVICE_IDENTIFIER)|(TARGET_DEVICE_MODEL)|(PRODUCT_BUNDLE_IDENTIFIER)' > "${scripts}/env.sh"
