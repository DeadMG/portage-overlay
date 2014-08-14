# Distributed under the terms of the GNU General Public License v2

EAPI=5

inherit versionator

DESCRIPTION="YouTrack issue tracker"
HOMEPAGE="http://www.jetbrains.com/youtrack/"

MY_PV="$(get_version_component_range 1-3)-$(get_version_component_range 4)"
MY_WAR="youtrack-${MY_PV}.war"
SRC_URI="http://download.jetbrains.com/charisma/${MY_WAR}"

LICENSE=""
SLOT="$(get_version_component_range 1-2)"
KEYWORDS="amd64"
IUSE=""

DEPEND=""
RDEPEND="${DEPEND}"

S="${WORKDIR}"

src_unpack() {
	true;
}

src_install() {
	dodir /usr/share/youtrack
	cp ${DISTDIR}/${MY_WAR} ${D}/usr/share/youtrack/youtrack-${SLOT}.war
}
