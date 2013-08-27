cloud_monitoring_entity "#{node.hostname}" do
  label                 "#{node.hostname}"
  agent_id              node['cloud_monitoring']['agent']['id']
  rackspace_username    node['cloud_monitoring']['rackspace_username']
  rackspace_api_key     node['cloud_monitoring']['rackspace_api_key']
  action :create
end


cloud_monitoring_check  "cpu" do
  type                  'agent.cpu'
  period                30
  timeout               10
  rackspace_username    node['cloud_monitoring']['rackspace_username']
  rackspace_api_key     node['cloud_monitoring']['rackspace_api_key']
  action :create
end

cloud_monitoring_check  "load" do
  type                  'agent.load_average'
  period                30
  timeout               10
  rackspace_username    node['cloud_monitoring']['rackspace_username']
  rackspace_api_key     node['cloud_monitoring']['rackspace_api_key']
  action :create
end

cloud_monitoring_check  "disk" do
  type                  'agent.disk'
  period                30
  timeout               10
  details              'target' => '/dev/xvda1'
  rackspace_username    node['cloud_monitoring']['rackspace_username']
  rackspace_api_key     node['cloud_monitoring']['rackspace_api_key']
  action :create
end

cloud_monitoring_check  "filesystem" do
  type                  'agent.filesystem'
  period                30
  timeout               10
  details               'target' => '/'
  rackspace_username    node['cloud_monitoring']['rackspace_username']
  rackspace_api_key     node['cloud_monitoring']['rackspace_api_key']
  action :create
end

cloud_monitoring_check  "public_network" do
  type                  'agent.network'
  period                30
  timeout               10
  details               'target' => 'eth0'
  rackspace_username    node['cloud_monitoring']['rackspace_username']
  rackspace_api_key     node['cloud_monitoring']['rackspace_api_key']
  action :create
end

cloud_monitoring_check  "private_network" do
  type                  'agent.network'
  period                30
  timeout               10
  details               'target' => 'eth1'
  rackspace_username    node['cloud_monitoring']['rackspace_username']
  rackspace_api_key     node['cloud_monitoring']['rackspace_api_key']
  action :create
end

cloud_monitoring_check  "ping" do
  target_alias          'access_ip1_v4'
  type                  'remote.ping'
  period                30
  timeout               4
  monitoring_zones_poll ['mzord','mzdfw', 'mziad']
  rackspace_username    node['cloud_monitoring']['rackspace_username']
  rackspace_api_key     node['cloud_monitoring']['rackspace_api_key']
  action :create
end

cloud_monitoring_alarm  "ping alarm" do
  check_label           'ping'
  criteria              "if (metric['available'] < 80) { return new AlarmStatus(CRITICAL, 'Packet loss is greater than 20%'); } if (metric['available'] < 95) {return new AlarmStatus(WARNING, 'Packet loss is greater than 5%');}return new AlarmStatus(OK, 'Packet loss is normal');"
  notification_plan_id  'npTechnicalContactsEmail'
  action :create
end

cloud_monitoring_alarm  "freespace" do
  check_label           'filesystem'
  criteria              "if (metric['avail'] > 2097000) { return new AlarmStatus(OK, 'More than 2GB of free space left.'); } if (metric['avail'] < 1048500) { return new AlarmStatus(CRITICAL, 'Less than 1GB of free space left.'); } if (metric['avail'] < 2097000 ) { return new AlarmStatus(WARNING, 'Less than 2GB of free space left.'); }" 
  notification_plan_id  'npTechnicalContactsEmail'
  action                :create
end










