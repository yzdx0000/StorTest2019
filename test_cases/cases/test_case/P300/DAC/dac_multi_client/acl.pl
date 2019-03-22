#!/usr/bin/perl -w 
use strict;
use Spreadsheet::ParseExcel;
use Data::Dumper;
#use Linux::ACL;
use Switch;

# my $is_init_ok;
our $workbook;
our @worksheet;
our $row_min;
our $row_max;
our $col_min;
our $col_max;
# our $file_sys_dir="/mnt/parastor";

our $win_ip="10.2.43.217";
# our $nfs_ip="10.2.42.79";
our $posix_ip=$ARGV[0];
our $nfs_ip=$ARGV[1];
our $tools_dir=$ARGV[2];
our $file_sys_dir=$ARGV[3];
our $nfs_sys_dir=$ARGV[4];                #add by zhanghan
our $dac_set_path=$ARGV[5];
our $is_init_ok=$ARGV[6];

our $pwd_dir=$ENV{'PWD'};
our $logfile="$pwd_dir\/logfile";

my ($u1, $u2, $u3, $u4);
my $do_mount_smb="C:/mount.bat;";
my $win_mount_point="X:/";
my @os_type=("posix", "nfs", "win");
# my @os_type=("posix");
# my @os_type=("win");

sub read_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd="cat $filename ";
	my $ret;
	my $action="su - $user -c '$cmd'";
	logmsg($action);
	$ret=sshv($node,$action);
	return $ret;
}

sub read_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd="ls $dirname ";
	my $ret;
	my $action="su - $user -c '$cmd'";
	logmsg($action);
	$ret=sshv($node,$action);
	return $ret;
}

sub write_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd="echo who >> $filename ";
	my $ret;
	my $action="su - $user -c '$cmd'";
	logmsg($action);
	$ret=sshv($node,$action);
	return $ret;
}

sub write_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd="touch $dirname/write_new";
	my $ret;
	my $action="su - $user -c '$cmd'";
	logmsg($action);
	$ret=sshv($node,$action);
	return $ret;
}

sub excute_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd="/$filename";
	my $ret;
	my $action="su - $user -c '$cmd'";
	logmsg($action);
	$ret=sshv($node,$action);
	return $ret;
}

sub excute_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd="cd  $dirname";
	my $ret;
	my $action="su - $user -c '$cmd'";
	logmsg($action);
	$ret=sshv($node,$action);
	return $ret;

}

sub remove_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd="rm -fr $filename";
	my $ret;
	my $action="su - $user -c '$cmd'";
	logmsg($action);
	$ret=sshv($node,$action);
	return $ret;

}

sub remove_dir{
        my ($node, $user,$defalut_dir, $dirname)=@_;
        my $cmd="rm -fr $dirname";
        my $ret;
        my $action="su - $user -c '$cmd'";
        logmsg($action);
        $ret=sshv($node,$action);
        return $ret;

}

####win deal with file
sub win_read_file{
    logmsg("win_read_file start...");
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="type $filename ";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

sub win_attrib_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="attrib $filename ";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

sub win_attrib_file_I{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="attrib -I $filename ";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

sub win_scontent_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="Set-Content $filename -Value \"hello\"";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

sub win_setacl_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="Set-Acl";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

sub win_getacl_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="Get-Acl $filename ";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

sub win_del_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="del $filename ";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

###win deal with dir
sub win_ls_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="ls $dirname && dir $dirname";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

sub win_wirte_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="Set-Content $dirname ";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

sub win_attrib_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="attrib $dirname ";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

sub win_attrib_dir_I{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="attrib $dirname ";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

sub win_setacl_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="attrib $dirname ";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

sub win_del_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="attrib $dirname ";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

sub win_get_acl_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="attrib $dirname ";
	my $ret=sshv_win($user,$win_ip,$cmd_win);
	return $ret;
}

my %action_type=(
	RF => \&read_file,
	RD => \&read_dir,
	WF => \&write_file,
	WD => \&write_dir,
	XF => \&excute_file,
	XD => \&excute_dir,
	DF => \&remove_file,
        DD => \&remove_dir
);

my %win_action=(
	rF => \&win_read_file,
	aF => \&win_attrib_file,
	AF => \&win_attrib_file_I,
	wF => \&win_scontent_file,
	CF => \&win_setacl_file,
	cF => \&win_getacl_file,
	DF => \&win_del_file,
	rD => \&win_ls_dir,
	wD => \&win_wirte_dir,
	aD => \&win_attrib_dir,
	AD => \&win_attrib_dir_I,
	CD => \&win_setacl_dir,
	cD => \&win_get_acl_dir,
	DD => \&win_del_dir,
);


sub logmsg
{
	my $date=`date +'%b %d %T'`;
	chomp($date);
	`touch $logfile`;
	my $msg='';
	foreach(@_){
		$msg.=" $_";
	}
	print $msg,"\n";
	$msg="$date  $msg";
	open FH, ">>$logfile";
	print FH $msg,"\n";
	close FH;
}

#convert the s to 0,  F to 1
sub convers_ret{
	my $para=shift;
	if(trim($para) =~ /S/i ){
		return 0;
	}elsif(trim($para) =~ /F/i){
		return 1;
	}else{
		return -1;
	}
}

sub sshv{
	my ($node,$cmd)=@_;
	return '' if ( $cmd eq '' ) ;
#	my $out = qx/ssh $node "$cmd" 2>&1/;
#	my $out = qx/ssh $node "$cmd" 2>\/dev\/null /;
        my $out = system("ssh $node \"$cmd\" 2>\/dev\/null") ;
	print $out;
	my $tmp=$?;
	if($tmp ne 0){
		$tmp=1;
	}
	chomp $out;
	logmsg($out);
	return $tmp;
}

sub sshv_win{
	my ($user,$node,$cmd)=@_;
    $cmd=$do_mount_smb.$cmd;
    logmsg("winssh: $cmd");
	return '' if ( $cmd eq '' );
	my $out = system("ssh $user\@$node $cmd");
	my $tmp=$?;
	if($tmp ne 0){
		$tmp=1;
	}
	chomp $out;
	logmsg($out);
	return $tmp;
}


#delete scpace at string start and end
sub  trim {
 	my $s = shift;
 	$s =~ s/^\s+|\s+$//g;
 	return $s
};

=pod
sub split_action{
	my $str_action=shift;
	my @str=split(/:/,$str_action);
	return \@str;
}
=cut

sub check_ret{
	my $ret=shift;
	if($ret ne 0){
		logmsg("the function ret is $ret,please check...");
		exit(0);
	}
}

sub add_user{
     $u1='u1';
     $u2='u2';
     $u3='u3';
     $u4='u4';
}

sub init_worksheets{
	my $parser	 = Spreadsheet::ParseExcel->new();
    #$workbook = $parser->parse('/root/ugo.xls');
    $workbook = $parser->parse("$pwd_dir/ugo.xls");

	if ( !defined $workbook ) {
		logmsg("no excle file exied");
		die $parser->error(), ".\n";
	}

	#return $workbook->worksheets();
}

#set the file use chmod
sub ugo_modify{
     my ($node, $user, $filename, $ugo)=@_;
	 my $cmd="chmod $ugo $filename";
	 my $ret;
	 my $action="su - $user -c '$cmd' ";
	 logmsg($action);
	 $ret=sshv($node,$action);
	 return $ret;
}

#set the file use chmod
sub creat_mode_file{
     my ($node, $user,$defalut_dir, $filename, $ugo)=@_;
	 # my $cmd="cd $defalut_dir && creatfile $filename $ugo";
	 my $cmd="cd $defalut_dir ; $tools_dir/tools/creatfile $filename $ugo";
         my $ret;
	 #my $action="su - $user -c '\"$cmd\"'";
	 my $action="su - $user -c '$cmd' ";
	 logmsg($action);
	 $ret=sshv($node,$action);
	 $ret=prepar_file($node, $user, "$defalut_dir/$filename");
	 return $ret;
}

#set the file use chmod
sub creat_mode_dir{
     my ($node, $user,$defalut_dir, $dirname, $ugo)=@_;
	 my $cmd="cd $defalut_dir ; mkdir -m $ugo $dirname";
	 my $ret;
	 #my $action="su - $user -c '\"$cmd\"'";
	 my $action="su - $user -c '$cmd'";
	 logmsg($action);
	 $ret=sshv($node,$action);
	 return $ret;
}

sub get_action_type_key{
	my ($ip,$username,$cmd,$dest_obj)=@_;
	my @tmp_cmd=split(/#/,$cmd);
	#if cmd is SD or SF. you neet to creat it
	logmsg("get_action_type_key:");
	print Dumper(@tmp_cmd);
	if($tmp_cmd[1] eq "SD"){
		 $dest_obj="${dest_obj}SD";
		 check_ret(prepar_dir($posix_ip, $username, $dest_obj));
		 $tmp_cmd[1]='D';
	}elsif($tmp_cmd[1] eq "SF"){
		 $dest_obj="${dest_obj}SF";
		 check_ret(prepar_file($posix_ip, $username, $dest_obj));
		 $tmp_cmd[1]='F';
	}
	my $do_mode=$tmp_cmd[0].$tmp_cmd[1];
	logmsg("get_action_type_key:do_mode: $do_mode");
	return $do_mode;
}


###################check########################
sub linux_check_ugo{
	logmsg("linux_check_ugo start");
	my ($username,$cmd_linux,$ret_normal,$defalut_dir,$dest_obj)=@_;
	logmsg("linux_check_ugo",$username,$cmd_linux,$ret_normal,$defalut_dir,$dest_obj);
	my $do_mode=get_action_type_key($posix_ip,$username,$cmd_linux,$dest_obj);
	#find the function in  %action_type
	logmsg("do_mode is $do_mode...");
	my $ret=$action_type{$do_mode}->($posix_ip,$username,$defalut_dir,$dest_obj);
	logmsg("linux_check_ugo: $cmd_linux: $ret\n");
	return $ret;
}

sub nfs_check_ugo{
        logmsg("nfs_check_ugo start");
	my ($username,$cmd_linux,$ret_normal,$defalut_dir,$dest_obj)=@_;
        logmsg("nfs_check_ugo",$username,$cmd_linux,$ret_normal,$defalut_dir,$dest_obj);
	my $do_mode=get_action_type_key($nfs_ip,$username,$cmd_linux,$dest_obj);

	#find the function in  %action_type
        logmsg("do_mode is $do_mode...");
	my $ret=$action_type{$do_mode}->($nfs_ip,$username,$defalut_dir,$dest_obj);
	logmsg("nfs_check_ugo: $cmd_linux: $ret\n");
	return $ret;
}

sub win_check_ugo{
	#my $str=shift;
	logmsg("win_check_ugo start \n");
	my ($username,$cmd_win,$ret_normal,$defalut_dir,$dest_obj)=@_;

	my $do_mode=get_action_type_key($win_ip,$username,$cmd_win,$dest_obj);
	#find the function in  %action_type
	logmsg("do_mode is $do_mode...");

	#$cmd_win=$do_mount_smb.$cmd_win;
	my $ret=$win_action{$do_mode}->($nfs_ip,$username,$defalut_dir,$dest_obj);
	return $ret;
}

##################set ugo###########################
sub setadv_normal_uacl{
	my ($ret, $cmd);
	my ($node, $owner, $user, $option,$is_inherit,$yn,$filename)=@_;
	if($is_inherit eq 1){
		$cmd="su - $owner -c '$dac_set_path -m u:$user:$option:fd:$yn $filename'";
	}elsif($is_inherit eq 0){
	    $cmd="su - $owner -c '$dac_set_path -m u:$user:$option:\:$yn $filename'";
	}

	logmsg($cmd);
    $ret=sshv($node,$cmd);
	if($ret ne 0){
		logmsg("setadv_acl: $cmd err..");
		exit(0);
	}
}

sub setadv_normal_gacl{
	my ($ret, $cmd);
	my ($node, $owner, $group, $option,$is_inherit,$yn,$filename)=@_;
	if($is_inherit eq 1){
		$cmd="su - $owner -c '$dac_set_path -m g:$group:$option:fd:$yn $filename'";

	}elsif($is_inherit eq 0){
	    $cmd="su - $owner -c '$dac_set_path -m g:$group:$option::$yn $filename'";
	}

	logmsg($cmd);
    $ret=sshv($node,$cmd);
	if($ret ne 0){
		logmsg("setadv_acl: $cmd err..");
		exit(0);
	}

}

#set owner group everyone
sub setadv_sepcal_uacl{
	my ($ret, $cmd);
	print Dumper(@_);
	my ($node, $owner, $key, $option,$is_inherit,$yn,$filename)=@_;
	if($is_inherit eq 1){
		$cmd="su - $owner -c '$dac_set_path -m $key\@:$option:fd:$yn $filename'";
	}elsif($is_inherit eq 0){
	    $cmd="su - $owner -c '$dac_set_path -m $key\@:$option:\:$yn $filename'";
	}
	logmsg($cmd);

	 $ret=sshv($node, $cmd);
	if($ret ne 0){
		logmsg("setadv_acl: $cmd err..");
		exit(0);
	}
}

=pod
sub posix_set_ugo{
	my $cmd=shift;

}

sub win_set_ugo{
	my $cmd=shift;

}

sub nfs_set_ugo{
	my $cmd=shift;

}


##creat a file with mode ugo
sub creat_mode_file{

}


##creat a dir with mode ugo
sub creat_mode_dir{

}
=cut
###############set acl##############################

sub init_ugo_file{
	my ($worksheet, $node, $user, $dir, $row_max)=@_;
	#my $cmd="su - $user  -c 'for i in {0..$row_max}; do mkdir $dir\/\$i; done'";
	#my $cmd="su - $user  -c 'mkdir -p 1'";
	#logmsg($node, $cmd);
    #my $ret=sshv($node,$cmd);

	for(my $i=0; $i<=3; $i++){
	     logmsg("the row_max is $row_max...");
         my $mode_name=$worksheet->get_cell( $i, 0 )->value();
         $mode_name=trim($mode_name);
         for(my $j=1; $j<=6; $j++){
			 my $cmd="su - $user -c 'mkdir -p $dir/$mode_name/$j'";
			 #	my $action="su - $user -c '$cmd'";
			 logmsg($cmd);
			 my $ret=sshv($node,$cmd);
			 if($ret ne 0){
				logmsg("the $cmd is err:$ret");
				exit(0);
			 }

		       switch ($j) {
						   case    [1]	 {
						      for my $os (@os_type){
						          check_ret(ugo_modify($node, $user, "$dir/$mode_name/$j",777));
								  for(my $k=0; $k<=30; $k++){
										check_ret(prepar_file($node, $user, "$dir/$mode_name/$j/${os}_file_${k}"));
										check_ret(ugo_modify($node, $user, "$dir/$mode_name/$j/${os}_file_${k}", $mode_name));
										#debug
										#exit(0);
									    }
						      }#end 2 for
						   }
						   case    [2]  {
						      check_ret(ugo_modify($node, $user, "$dir/$mode_name/$j",777));
						      for my $os (@os_type){
						   		for(my $k=0; $k<=30; $k++){
									check_ret(prepar_dir($node, $user, "$dir/$mode_name/$j/${os}_dir_${k}"));
									check_ret(ugo_modify($node, $user, "$dir/$mode_name/$j/${os}_dir_${k}", $mode_name));
								}
						     }#end 2 for
						   }
						   case    [3]  {
								check_ret(prepar_dir($node, $user, "$dir/$mode_name/$j/testdir"));
								check_ret(ugo_modify($node, $user, "$dir/$mode_name/$j/testdir",777));
								setadv_sepcal_uacl($posix_ip, $u1, 'owner', "rwpxdDaARWcCoS",1,"allow","$dir/$mode_name/$j/testdir");
								setadv_sepcal_uacl($posix_ip, $u1, 'group', "-wpxdDa-RW----",1,"allow","$dir/$mode_name/$j/testdir");
								setadv_sepcal_uacl($posix_ip, $u1, 'everyone', "-wpx--Da-RW---",1,"allow","$dir/$mode_name/$j/testdir");
								setadv_normal_uacl($posix_ip, $u1, $u2, "rwpxdDaARWc--S",1,"allow","$dir/$mode_name/$j/testdir");
								setadv_normal_uacl($posix_ip, $u1, $u3, "-----D--------",1,"allow","$dir/$mode_name/$j/testdir");
								for my $os (@os_type){
						   			for(my $k=0; $k<=30; $k++){
										check_ret(creat_mode_file($node, $user, "$dir/$mode_name/$j/testdir/","${os}_file_${k}", $mode_name));
									}
								}
						   }

						   case    [4]  {
						   		check_ret(prepar_dir($node, $user, "$dir/$mode_name/$j/testdir"));
						   		check_ret(ugo_modify($node, $user, "$dir/$mode_name/$j/testdir",777));
								setadv_sepcal_uacl($posix_ip, $u1, 'owner', "rwpxdDaARWcCoS",1,"allow","$dir/$mode_name/$j/testdir");
								setadv_sepcal_uacl($posix_ip, $u1, 'group', "-wpxdDa-RW----",1,"allow","$dir/$mode_name/$j/testdir");
								setadv_sepcal_uacl($posix_ip, $u1, 'everyone', "-wpx--Da-RW---",1,"allow","$dir/$mode_name/$j/testdir");
								setadv_normal_uacl($posix_ip, $u1, $u2, "rwpxdDaARWc--S",1,"allow","$dir/$mode_name/$j/testdir");
								setadv_normal_uacl($posix_ip, $u1, $u3, "-----D--------",1,"allow","$dir/$mode_name/$j/testdir");
								for my $os (@os_type){
						   			for(my $k=0; $k<=30; $k++){
										creat_mode_dir($node, $user, "$dir/$mode_name/$j/testdir/","${os}_dir_${k}", $mode_name);
									}
								}

						   }
						   case    [5]	 {
						   		for my $os (@os_type){
						   			for(my $k=0; $k<=30; $k++){
										check_ret(prepar_file($node, $user, "$dir/$mode_name/$j/${os}_file_${k}"));
										check_ret(ugo_modify($node, $user, "$dir/$mode_name/$j/${os}_file_${k}", $mode_name));
										setadv_sepcal_uacl($posix_ip, $u1, 'owner', "rwpx-DaARWcCoS",0,"allow","$dir/$mode_name/$j/${os}_file_${k}");
										setadv_sepcal_uacl($posix_ip, $u1, 'group', "-wp--Da-RW----",0,"allow","$dir/$mode_name/$j/${os}_file_${k}");
										setadv_sepcal_uacl($posix_ip, $u1, 'everyone', "-wp--Da-RW----",0,"allow","$dir/$mode_name/$j/${os}_file_${k}");
										setadv_normal_uacl($posix_ip, $u1, $u2, "rwpx-DaARWc--S",0,"allow","$dir/$mode_name/$j/${os}_file_${k}");
										setadv_normal_uacl($posix_ip, $u1, $u3, "-----D--------",0,"allow","$dir/$mode_name/$j/${os}_file_${k}");
									}
								}
						   }
						   case    [6]   {
						      for my $os (@os_type){
						   			for(my $k=0; $k<=30; $k++){
								  	check_ret(prepar_dir($node, $user, "$dir/$mode_name/$j/${os}_dir_${k}"));
									check_ret(ugo_modify($node, $user, "$dir/$mode_name/$j/${os}_dir_${k}", $mode_name));
									setadv_sepcal_uacl($posix_ip, $u1, 'owner', "rwpxdDaARWcCoS",0,"allow","$dir/$mode_name/$j/${os}_dir_${k}");
									setadv_sepcal_uacl($posix_ip, $u1, 'group', "-wpx-Da-RW----",0,"allow","$dir/$mode_name/$j/${os}_dir_${k}");
									setadv_sepcal_uacl($posix_ip, $u1, 'everyone', "-wpx-Da-RW----",0,"allow","$dir/$mode_name/$j/${os}_dir_${k}");
									setadv_normal_uacl($posix_ip, $u1, $u2, "rwpxdDa-RWc--S",0,"allow","$dir/$mode_name/$j/${os}_dir_${k}");
									setadv_normal_uacl($posix_ip, $u1, $u3, "-----D--------",0,"allow","$dir/$mode_name/$j/${os}_dir_${k}");
						   		}
						   	  }
						   }
						   else 	   { logmsg("$j is 0 or err...");
						   				  exit(-1);
						   			   }
					}#end case

         }#end for j
	}#end for i
	return 0;
}#end for function

sub prepar_file{
    my ($node, $user, $filename)=@_;
    my $cmd="echo \\#\\! /bin/bash >> $filename";
    my $ret;
    if($node eq $win_ip){
		$ret=sshv_win($user,$node,$cmd);
    }else{
	#	my $action="\"su - $user -c $cmd\"";
	#	logmsg($action);
	#	my $send_cmd="ssh $node $action";
	#	logmsg($send_cmd);
	#	$ret=system($send_cmd);
                my $action="su - $user -c '$cmd'";
        	        $ret=sshv($node,$action);
    }
    return $ret;
}

sub prepar_dir{
    my ($node, $user, $dirname)=@_;
    my $cmd="mkdir $dirname";
    my $ret;
    if($node eq $win_ip){
		$ret=sshv_win($user,$node,$cmd);
    }else{
		my $action="su - $user -c '$cmd'";
	    $ret=sshv($node,$action);
    }
     return $ret;
}

sub is_ret_corret{
	my ($ret_normal, $ret)=@_;
	if(((trim($ret_normal) eq 'S') &&($ret eq 0))||((trim($ret_normal) eq 'F') && ($ret ne 0))){
		return 0;
	}else{
		return -1;
	}
}

#deal with each of cells
sub deal_with_cell{
	logmsg "deal_with_cell start \n";
	my ($cell,$funcion_check,$defalut_dir,$type_file,$os)=@_;
	my @cell_str = split(/\n/, $cell->value());
	@cell_str = grep(/^[#]/, @cell_str);
	#print Dumper(@cell_str);
	my $i=0;
	for my $each_action (@cell_str){
			logmsg($each_action);
   		    my @tmp=split(/:/,$each_action);
			my $username=$tmp[0];
			my $cmd=$tmp[1];
			my $ret_normal=$tmp[2];
			$username=~ s/#//;

			print "this is $each_action\n";
			print "username:$username \n";
			#print "cmd:$cmd_linux \n";
			print "ret:$ret_normal \n";
			my $dest_obj="$defalut_dir/${os}_${type_file}_${i}";
			logmsg("the $dest_obj will be deal...");

			my $ret=&$funcion_check(trim($username),trim($cmd),trim($ret_normal),$defalut_dir,$dest_obj);
			if(is_ret_corret($ret_normal,$ret) ne 0){
				logmsg("$each_action err: $ret_normal != $ret...");
				exit(1);
			}
			$i++;
	}
}

sub check_nfs_mode_sheet{
	logmsg("nfs_mode start\n");
	my $worksheet=shift;

	my ( $row_min, $row_max ) = $worksheet->row_range();
	my ( $col_min, $col_max ) = $worksheet->col_range();
	logmsg("Row, Col = ($row_max, $col_max)\n");
	#print "Value	  = ", ($worksheet->get_cell( 7, 2 ))->value(),		 "\n";
	#creat the parent dir
	my $owner=$u1;
	#my $node=$nfs_ip;
        my $node=$posix_ip;
	#debug
	if($is_init_ok == 1){
		my $ret = init_ugo_file($worksheet,$node,$owner,$file_sys_dir,$row_max);
		logmsg("========init_ugo_file end:$ret=======");
       	#	exit(0);
	}
	#exit(0);$col_max
	for my $row ( 0 .. 3 ) {
				#debug col
				for my $col ( 1 .. 12 ) {
				   logmsg("------------------------this is the $row - $col checking--------------------------");
				   my $cell = $worksheet->get_cell( $row, $col );
				   logmsg("Value	   = ", $cell->value(), 	  "\n");

				   my $mode_name=$worksheet->get_cell( $row, 0 )->value();
                   $mode_name=trim($mode_name);
                   my $tmp_col=$col%6;
                   if($tmp_col eq 0){
						$tmp_col=6;
                   }
				   my $defalt_dir="$file_sys_dir/$mode_name/$tmp_col/";
                                   my $nfs_defalt_dir="$nfs_sys_dir/$mode_name/$tmp_col/";  # add by zhanghan
				   my $type_file;
				   my $os;
				   switch ($col) {
						   case    [1,2,5,6]	 {
								my $func_ref = \&linux_check_ugo;
							    logmsg("now dir is $row $col:$defalt_dir...");
							    if($col%2 eq 0){
									#$defalt_dir=$defalt_dir."dir";
									$type_file="dir";
							    }else{
									$type_file="file";
							    }
								deal_with_cell($cell, $func_ref,$defalt_dir,$type_file,$os_type[0]);
						   }
						   case    [3,4]  {
								my $func_ref = \&linux_check_ugo;
								$defalt_dir="$file_sys_dir/$mode_name/$tmp_col/testdir/";
							    if($col%2 eq 0){
									$type_file="dir";
							    }else{
									$type_file="file";
							    }
							    logmsg("now dir is $col:$defalt_dir...");
								deal_with_cell($cell, $func_ref,$defalt_dir,,$type_file,$os_type[0]);
						   }
						   case    [7,8,11,12]  {
								my $func_ref = \&nfs_check_ugo;
							    logmsg("now dir is $col:$nfs_defalt_dir...");
							    if($col%2 eq 0){
									$type_file="dir";
							    }else{
									$type_file="file";
							    }
								deal_with_cell($cell, $func_ref,$nfs_defalt_dir,$type_file,$os_type[1]);
						   }
						   case    [9, 10]  {
								my $func_ref = \&nfs_check_ugo;
								$nfs_defalt_dir="$nfs_sys_dir/$mode_name/$tmp_col/testdir/";
							    logmsg("now dir is $col:$nfs_defalt_dir...");
							    if($col%2 eq 0){
									$type_file="dir";
							    }else{
									$type_file="file";
							    }
								deal_with_cell($cell, $func_ref,$nfs_defalt_dir,$type_file,$os_type[1]);
						   }
						   case    [15,16]	 {
							   #nfs_check_ugo();
							   $defalt_dir="$file_sys_dir/$mode_name/$tmp_col/testdir/";
							   $defalt_dir=$win_mount_point.$defalt_dir;
							   logmsg("now dir is $col:$defalt_dir...");
							   if($col%2 eq 0){
									$type_file="dir";
							    }else{
									$type_file="file";
							    }
							   my $func_ref = \&win_check_ugo;
							   deal_with_cell($cell, $func_ref,$defalt_dir,$type_file,$os_type[2]);
						   }
						   case    [13, 14, 17, 18]   {
							   my $func_ref = \&win_check_ugo;
							   $defalt_dir="$mode_name/$tmp_col/";
							   $defalt_dir=$win_mount_point.$defalt_dir;
							   logmsg("now dir is $col:$defalt_dir...");
							    if($col%2 eq 0){
									$type_file="dir";
							    }else{
									$type_file="file";
							    }
							   deal_with_cell($cell, $func_ref,$defalt_dir,$type_file,$os_type[2]);
						   }
						   else 	   {
						   		logmsg("nfs_ugo_check: $cell is err");
						   		exit(-1);
						   }
					}
				  # print "Row, Col   = ($row, $col)\n";
				  #	print "Value	  = ", $cell->value(),		 "\n";
				  #	print "Unformatted = ", $cell->unformatted(), "\n";
				  #	print "\n";
				   next unless $cell;

				}#end [for 2]
			}#end [for 1]

}
sub client_mode{
	logmsg("client_mode start\n");
	my $worksheet=shift;

	my ( $row_min, $row_max ) = $worksheet->row_range();
	my ( $col_min, $col_max ) = $worksheet->col_range();
	logmsg("Row, Col = ($row_max, $col_max)\n");
	#print "Value	  = ", ($worksheet->get_cell( 7, 2 ))->value(),		 "\n";

}

sub get_sheet{
	#for my $worksheet ( $workbook->worksheets() ) {
	my $worksheet_count = $workbook->worksheet_count();
	logmsg("$worksheet_count  \n");
	##test###
	for(my $i=0; $i<=$worksheet_count-1;$i++){
	    $worksheet[$i]=$workbook->worksheet($i);
		#my $cell = $worksheet->get_cell(7, 2);
	    #print "Row, Col	= ($row, $col)\n";
		#print "Value	   = ", $cell->value(), 	  "\n";
		#print "Unformatted = ", $cell->unformatted(), "\n";
		#print "\n";
#		my @cell_str = split(/\n/, $cell->unformatted());
		# Loop reads cell in row(first) col(later) way
		if($i eq 0){
			check_nfs_mode_sheet($worksheet[0]);
		}
		if($i eq 1){
			#client_mode($worksheet[1]);
		}

	}
}

sub main{
	print "before you check the file, you must init the file
			now please input a number to execute:
			1: now init the file.
			2: now check the file.
			\n";
#	my $is_init_ok = <STDIN>;
#        $is_init_ok = <STDIN>;
	if($is_init_ok == 1){
		print "init the file start:";
	}else{
		print "check the file start:";
	}
	`> $logfile`;
	add_user();
	init_worksheets();
	get_sheet();
}
main;
