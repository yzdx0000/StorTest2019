/***
author:duyuli
date:2019-03-11
usage:cancel jenkins building(取消jenkins正在构建的任务)
**/

jobname_list = ['Stortest_priority_duyuli']
slave_name_list = ['10.2.42.154', '10.2.42.41']
def slave_list = hudson.model.Hudson.instance.slaves
def idle = 0
for (slave in slave_list){
    if (!slave.getComputer().isOffline() && slave_name_list.contains(slave.name) && !slave.getComputer().countBusy()){
        idle = 1;
        break;
    }
}
sleep(10000)
if (idle == 0){
    for (jobname in jobname_list){
        def job = Jenkins.instance.getItemByFullName(jobname)
        def flag = 0;
        for (build in job.builds) {
          if (!build.isBuilding()) { continue; }
          for (variable in build.getBuildVariables()) {
            if (variable.key == 'build_priority' && variable.value == '3'){
              build.doStop();
              flag = 1;
              break;
            }
          }
          if (flag) { break; }
        }
    }
}
