# Copyright 1999-2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=5

DESCRIPTION="LLVM & Clang for Wide"
HOMEPAGE="http://llvm.org"
SRC_URI="http://llvm.org/releases/${PV}/llvm-${PV}.src.tar.xz
	http://llvm.org/releases/${PV}/cfe-${PV}.src.tar.xz"

LICENSE="GPL-2"
SLOT="0/3.5"
KEYWORDS="~amd64 ~arm ~ppc ~ppc64 ~sparc ~x86 ~amd64-fbsd ~x86-fbsd ~x64-freebsd ~amd64-linux ~arm-linux ~x86-linux ~ppc-macos ~x64-macos"
DEPEND=">=app-arch/xz-utils
	>=sys-devel/make-3.81"

src_unpack() {
    default

    mv "${WORKDIR}"/cfe-${PV}.src "${S}"/tools/clang
}

src_configure() {
    mkdir -p ./build
    cd ./build
    ../configure --disable-terminfo --enable-targets="x86_64, x86"
}

src_compile() {
    cd ./build
    emake REQUIRES_RTTI=1
}