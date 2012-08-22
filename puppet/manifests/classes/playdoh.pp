# Project specific setup
# TODO: Make this rely on things that are not straight-up exec.
class playdoh ($project_path, $project_name, $password){

  $settings_file = "$project_path/settings_local.py"

  file { $settings_file:
    ensure => file,
    source => "$project_path/settings_local.py-dist",
    replace => false;
  }

  exec { "create_mysql_database":
    command => "mysql -uroot -p$password -B -e'CREATE DATABASE `$project_name` CHARACTER SET utf8;'",
    unless  => "mysql -uroot -p$password  -B --skip-column-names -e 'show databases' | /bin/grep '$project_name'",
    require => File[$settings_file]
  }

  exec { "grant_mysql_database":
    command => "mysql -uroot -p$password  -B -e \"GRANT ALL PRIVILEGES ON *.* TO '$project_name'@'localhost' IDENTIFIED BY '$project_name'\"",
    unless  => "mysql -uroot -p$password -B --skip-column-names mysql -e 'select user from user' | grep '$project_name'",
    require => Exec["create_mysql_database"];
  }

  exec { "syncdb":
    cwd => "$project_path",
    command => "python manage.py syncdb --noinput",
    require => Exec["grant_mysql_database"];
  }

  exec { "migrations":
    cwd => "$project_path",
    command => "python manage.py migrate",
    require => Exec["syncdb"];
  }

}
