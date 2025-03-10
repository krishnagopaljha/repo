import os
import shutil

# List of BeEF-XSS files and directories to delete
beef_files = [
    "/etc/beef-xss", "/etc/beef-xss/config.yaml", "/home/kali/beef",
    "/usr/bin/beef", "/usr/bin/beef-xss", "/usr/bin/beef-xss-stop",
    "/usr/lib/python3/dist-packages/faraday_plugins/plugins/repo/beef",
    "/usr/lib/python3/dist-packages/faraday_plugins/plugins/repo/beef/_init_.py",
    "/usr/lib/python3/dist-packages/faraday_plugins/plugins/repo/beef/_pycache_",
    "/usr/lib/python3/dist-packages/faraday_plugins/plugins/repo/beef/plugin.py",
    "/usr/lib/systemd/system/beef-xss.service", "/usr/share/beef-xss",
    "/usr/share/applications/kali-beef-xss-stop.desktop",
    "/usr/share/applications/kali-beef-xss.desktop",
    "/usr/share/desktop-directories/14-08-beef-service.directory",
    "/usr/share/doc/beef", "/usr/share/doc/beef-xss",
    "/usr/share/doc/beef/NEWS.gz", "/usr/share/doc/beef/changelog.Debian.amd64.gz",
    "/usr/share/doc/beef/changelog.Debian.gz", "/usr/share/doc/beef/copyright",
    "/usr/share/doc/python3-networkx/html/_downloads/79beefddd68fa45123e60db5559f52aa",
    "/usr/share/doc/python3-networkx/html/_downloads/79beefddd68fa45123e60db5559f52aa/plot_basic.py",
    "/usr/share/icons/Flat-Remix-Blue-Dark/apps/scalable/beef-xss.svg",
    "/usr/share/icons/Flat-Remix-Blue-Dark/apps/scalable/deadbeef.svg",
    "/usr/share/icons/Flat-Remix-Blue-Dark/apps/scalable/kali-beef-xss.svg",
    "/usr/share/icons/Flat-Remix-Blue-Dark/panel/deadbeef-panel.svg",
    "/usr/share/icons/Flat-Remix-Blue-Light/panel/deadbeef-panel.svg",
    "/usr/share/icons/hicolor/16x16/apps/kali-beef-xss-stop.png",
    "/usr/share/icons/hicolor/16x16/apps/kali-beef-xss.png",
    "/usr/share/icons/hicolor/22x22/apps/kali-beef-xss-stop.png",
    "/usr/share/icons/hicolor/22x22/apps/kali-beef-xss.png",
    "/usr/share/icons/hicolor/24x24/apps/kali-beef-xss-stop.png",
    "/usr/share/icons/hicolor/24x24/apps/kali-beef-xss.png",
    "/usr/share/icons/hicolor/256x256/apps/kali-beef-xss-stop.png",
    "/usr/share/icons/hicolor/256x256/apps/kali-beef-xss.png",
    "/usr/share/icons/hicolor/32x32/apps/kali-beef-xss-stop.png",
    "/usr/share/icons/hicolor/32x32/apps/kali-beef-xss.png",
    "/usr/share/icons/hicolor/48x48/apps/kali-beef-xss-stop.png",
    "/usr/share/icons/hicolor/48x48/apps/kali-beef-xss.png",
    "/usr/share/icons/hicolor/scalable/apps/kali-beef-xss-stop.svg",
    "/usr/share/icons/hicolor/scalable/apps/kali-beef-xss.svg",
    "/usr/share/kali-menu/applications/kali-beef-xss-stop.desktop",
    "/usr/share/kali-menu/applications/kali-beef-xss.desktop",
    "/usr/share/lintian/overrides/beef-xss", "/usr/share/man/man1/beef.1.gz",
    "/var/cache/apt/archives/beef-xss_0.5.4.0+git20220823-0kali3_amd64.deb",
    "/var/lib/beef-xss", "/var/lib/dpkg/info/beef-xss.conffiles",
    "/var/lib/dpkg/info/beef-xss.list", "/var/lib/dpkg/info/beef-xss.md5sums",
    "/var/lib/dpkg/info/beef-xss.postinst", "/var/lib/dpkg/info/beef-xss.postrm",
    "/var/lib/dpkg/info/beef-xss.prerm", "/var/lib/dpkg/info/beef.list",
    "/var/lib/dpkg/info/beef.md5sums",
    "/var/lib/systemd/deb-systemd-helper-enabled/beef-xss.service.dsh-also",
    "/var/lib/systemd/deb-systemd-helper-enabled/multi-user.target.wants/beef-xss.service"
]

def delete_path(path):
    """Forcefully delete a file or directory"""
    try:
        if os.path.isdir(path):  # If it's a directory, delete recursively
            shutil.rmtree(path)
            print(f"[DELETED] Directory: {path}")
        elif os.path.isfile(path) or os.path.islink(path):  # If it's a file or symlink, remove it
            os.remove(path)
            print(f"[DELETED] File: {path}")
        else:
            print(f"[NOT FOUND] {path}")
    except Exception as e:
        print(f"[ERROR] Failed to delete {path}: {e}")

if __name__ == "__main__":
    for file_path in beef_files:
        delete_path(file_path)
    
    print("\n[INFO] BeEF-XSS cleanup completed!")
