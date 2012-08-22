class elasticsearch($project_path) {
  $elasticsearch_deb = "https://github.com/downloads/elasticsearch/elasticsearch/elasticsearch-0.19.8.deb"

  exec { "elasticsearch-download":
    command => "wget $elasticsearch_deb",
    creates  =>  "/tmp/elasticsearch-0.19.8.deb",
    cwd => "/tmp/";
  }

  package { "elasticsearch":
    provider => dpkg,
    ensure => latest,
    source => "/tmp/elasticsearch-0.19.8.deb",
    require => [Package["openjdk-6-jre-headless"],
                Exec["elasticsearch-download"]];
  }

  service { "elasticsearch":
    ensure => running,
    enable => true,
    hasrestart => true,
    require => Package["elasticsearch"];
  }

}
