class sun_java_6 {

  $release = regsubst(generate("/usr/bin/lsb_release", "-s", "-c"), '(\w+)\s', '\1')

  file { "partner.list":
    path => "/etc/apt/sources.list.d/partner.list",
    ensure => file,
    owner => "root",
    group => "root",
    content => "deb http://archive.canonical.com/ $release partner\ndeb-src http://archive.canonical.com/ $release partner\n",
    notify => Exec["apt-get-update"],
  }

  exec { "apt-get-update":
    command => "/usr/bin/apt-get update",
    refreshonly => true,
  }

  package { "openjdk-6-jdk":
    ensure => latest,
    require => [ File["partner.list"], Exec["apt-get-update"] ],
  }

  package { "openjdk-6-jre":
    ensure => latest,
    require => [ File["partner.list"], Exec["apt-get-update"] ],
  }

}
