#!/usr/bin/perl -w
use strict;
use Spreadsheet::ParseExcel;
use Data::Dumper;
use feature "switch";


#use utf8::all;

our $workbook;
our @worksheet;
our $row_min;
our $row_max;
our $col_min;
our $col_max;
our $file_sys_dir="/mnt/zhanghan";  #factualy doesn't take effect,comment by zhanghan 20181114

our $win_ip="10.2.43.217";   #factualy doesn't take effect,comment by zhanghan 20181114
# our $nfs_ip="10.2.42.79"; //annotated by zhanghan 20181114
our $posix_ip="10.2.42.80";  #factualy doesn't take effect,comment by zhanghan 20181114

our $pwd_dir=$ARGV[0];
my $u1_addr=$ARGV[1];
my $u2_addr=$ARGV[2];
my $u3_addr=$ARGV[3];
my $u4_addr=$ARGV[4];
our $test_dir=$ARGV[5];

our $logfile="$pwd_dir\\logfile_win";

my ($u1, $u2, $u3, $u4);	
my $do_mount_smb="C:/mount.bat;";
my $win_mount_point="Z:/";
my @os_type=("posix", "nfs", "win");
my $pwspath = "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe";
my %user_dir=(
	"u1" => $u1_addr,
	"u2" => $u2_addr,
	"u3" => $u3_addr,
	"u4" => $u4_addr,
);

my $win_passwd="parastor;123";  #factualy doesn't take effect,comment by zhanghan 20181114
####win deal with file
sub win_read_file{
    logmsg("win_read_file start...");
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="type $filename ";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_read_file:$ret");
	return $ret;
}

sub win_attrib_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="attrib $filename ";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_attrib_file:$ret");
	return $ret;
}

sub win_attrib_file_I{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="attrib -I $filename ";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_attrib_file_I:$ret");
	return $ret;
}

sub win_scontent_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="Set-Content $filename -Value \"hello\"";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_scontent_file:$ret");
	return $ret;
}

sub win_setacl_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="Set-Acl";
	#my $ret=win_exe($user,$win_passwd,$cmd_win);
	my $ret=0;
	return $ret;
}

sub win_getacl_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="Get-Acl $filename ";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_getacl_file:$ret");
	return $ret;
}

sub win_del_file{
	my ($node, $user,$defalut_dir, $filename)=@_;
	my $cmd_win="del $filename ";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_del_file:$ret");
	return $ret;
}

###win deal with dir
sub win_ls_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="dir $dirname";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_ls_dir:$ret");
	return $ret;
}

sub win_wirte_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="New-Item $dirname\\testfile -type file";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_wirte_dir:$ret");
	return $ret;
}

sub win_attrib_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="attrib $dirname ";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_attrib_dir:$ret");
	return $ret;
}

sub win_attrib_dir_I{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="attrib +I $dirname ";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_attrib_dir_I:$ret");
	return $ret;
}

sub win_setacl_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="attrib $dirname ";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_setacl_dir:$ret");
	return $ret;
}

sub win_del_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="del $dirname ";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_del_dir:$ret");
	return $ret;
}

sub win_get_acl_dir{
	my ($node, $user,$defalut_dir, $dirname)=@_;
	my $cmd_win="Get-Acl $dirname ";
	my $ret=win_exe($user,$win_passwd,$cmd_win);
	logmsg("win_get_acl_dir:$ret");
	return $ret;
}

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
	#my $date=`date`;
	#chomp($date);

	#`echo $date >> $logfile`;
	foreach(@_){
	    print "$_\n";
		`echo $_ >>$logfile`;
	}
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

#delete scpace at string start and end
sub  trim {
 	my $s = shift;
 	$s =~ s/^\s+|\s+$//g;
 	return $s
};

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
   # $workbook = $parser->parse('c:/ugo.xls');
        $workbook = $parser->parse("$pwd_dir/ugo.xls");

	if ( !defined $workbook ) {
		logmsg("no excle file exied");
		die $parser->error(), ".\n";
	}

	#return $workbook->worksheets();
}
sub get_action_type_key{
	my ($ip,$username,$cmd,$dest_obj)=@_;
	my @tmp_cmd=split(/#/,$cmd);
	#if cmd is SD or SF. you neet to creat it
	#logmsg("get_action_type_key:");
	print Dumper(@tmp_cmd);
	if($tmp_cmd[1] eq "SD"){
		 $dest_obj="${dest_obj}SD";
		 check_ret(prepar_dir_win($posix_ip, $username, $dest_obj));
		 $tmp_cmd[1]='D';
	}elsif($tmp_cmd[1] eq "SF"){
		 $dest_obj="${dest_obj}SF";
		 check_ret(prepar_file_win($posix_ip, $username, $dest_obj));
		 $tmp_cmd[1]='F';
	}
	my $do_mode=$tmp_cmd[0].$tmp_cmd[1];
	logmsg("get_action_type_key:do_mode: $do_mode");
	return $do_mode;
}


###################check########################
sub win_check_ugo{
	logmsg("win_check_ugo start \n");
	my ($username,$cmd_win,$ret_normal,$defalut_dir,$dest_obj)=@_;

	my $do_mode=get_action_type_key($win_ip,$username,$cmd_win,$dest_obj);
	#find the function in  %action_type
	logmsg("do_mode is $do_mode...");

	#$cmd_win=$do_mount_smb.$cmd_win;
	my $ret=$win_action{$do_mode}->($win_ip,$username,$defalut_dir,$dest_obj);
	return $ret;
}
###############set acl##############################

sub init_ugo_file{
	return 0;
}#end for function

sub prepar_dir_win{
    my ($user, $filename)=@_;
    my $cmd="'New-Item $filename -type Directory'";
	system("$pwspath -command $cmd");
    return $?;
}

sub prepar_file_win{
    my ($user, $filename)=@_;
    my $cmd="'New-Item $filename -type File'";
	system("$pwspath -command $cmd");
    return $?;
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

			logmsg("this is $each_action\n");
			logmsg("username:$username \n");
			logmsg("ret:$ret_normal \n");
			logmsg($user_dir{$username});
            my $defalut_dir_tmp=$user_dir{"$username"}.$defalut_dir;
            logmsg("start_winexe:defalut_dir:$defalut_dir_tmp\n");
			my $dest_obj="$defalut_dir_tmp\\${os}_${type_file}_${i}";
			logmsg("the $dest_obj will be deal...");

			my $ret=&$funcion_check(trim($username),trim($cmd),trim($ret_normal),$defalut_dir_tmp,$dest_obj);
			if(is_ret_corret($ret_normal,$ret) ne 0){
				logmsg("$each_action err: $ret_normal != $ret...");
				exit(1);
			}
			$i++;
	}
}

sub check_nfs_mode_sheet{
	#logmsg("nfs_mode start\n");
	my $worksheet=shift;

	my ( $row_min, $row_max ) = $worksheet->row_range();
	my ( $col_min, $col_max ) = $worksheet->col_range();
	#logmsg("Row, Col = ($row_max, $col_max)\n");
	#print "Value	  = ", ($worksheet->get_cell( 7, 2 ))->value(),		 "\n";
	#creat the parent dir
	my $owner=$u1;
	# my $node=$nfs_ip;   #annotated by zhanghan 20181114
	for my $row ( 0 .. 3 ) {
				#debug col
				for my $col ( 13 .. $col_max ) {
        # for my $col ( 15 .. 15 ) {
				  # logmsg("------------------------this is the $row - $col checking--------------------------");
				   my $cell = $worksheet->get_cell( $row, $col );
				  logmsg($cell->value());

				   my $mode_name=$worksheet->get_cell( $row, 0 )->value();
                   $mode_name=trim($mode_name);
                   my $tmp_col=$col%6;
                   if($tmp_col eq 0){
						$tmp_col=6;
                   }
				   my $defalt_dir="\\$test_dir\\$mode_name\\$tmp_col\\";
				   my $type_file;
				   my $os;
				   if($col eq 15 || $col eq 16){
										   $defalt_dir="\\$test_dir\\$mode_name\\$tmp_col\\testdir\\";
										   if($col%2 eq 0){
												$type_file="dir";
											}else{
												$type_file="file";
											}
										   my $func_ref = \&win_check_ugo;
										   deal_with_cell($cell, $func_ref,$defalt_dir,$type_file,$os_type[2]);

				   }elsif($col eq 13 || $col eq 14 || $col eq 17 || $col eq 18){
					  								 my $func_ref = \&win_check_ugo;
													 # $defalt_dir="$mode_name/$tmp_col/";
													 # $defalt_dir=$win_mount_point.$defalt_dir;
													   if($col%2 eq 0){
														   $type_file="dir";
													   }else{
														   $type_file="file";
													   }
													  deal_with_cell($cell, $func_ref,$defalt_dir,$type_file,$os_type[2]);

				   }else{
						exit(0);
				   }
				  # print "Row, Col   = ($row, $col)\n";
				  #	print "Value	  = ", $cell->value(),		 "\n";
				  #	print "Unformatted = ", $cell->unformatted(), "\n";
				  #	print "\n";
				   next unless $cell;

				}#end [for 2]
			}#end [for 1]

}

sub get_sheet{
	#for my $worksheet ( $workbook->worksheets() ) {
	my $worksheet_count = $workbook->worksheet_count();
	#logmsg("$worksheet_count  \n");
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

sub win_exe{
	my ($username,$passwd,$cmd)=@_;
    #system("$pwspath -command echo $cmd > c:/.ps1");
    #my $cmd_ps_path="C:/Users/Public/execute.ps1";
	#my $result = `$pwspath -command $cmd_ps_path \"$username\"  \"$passwd\"`;
	#system("$pwspath -command $cmd_ps_path $username");
	#logmsg($result);
	#print $result;
	#logmsg("$?");
	my $ret=system("$pwspath -command $cmd");
	my $is_ok=$?;
    logmsg("$ret\n");
    return $is_ok;
}

sub main{
	`echo "start" > $logfile`;
	add_user();
	init_worksheets();
	get_sheet();

}
main();

