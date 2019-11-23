#!/bin/bash
LocalRepositories="/d/CCPD-G8.6/Python3-WebApp"
cd $LocalRepositories

git status -s

read -r -p "继续提交？ [Y/N] " input1

case $input1 in 
	[yY][eE][sS]|[yY])
		echo "开始提交......"
		git pull
		echo "Pull 成功。"
		git add -A
		echo "Add 成功。"
		read -p "请输入Commit信息:" input2
		git commit -m $input2
		echo "Commit 成功。"
		git push -u origin master
		echo "Push 成功。"
		#脚本参数
		#git commit -m $1
		#git push -u origin $2
		;;
    [nN][oO]|[nN])
		echo "中断提交!"
		exit 1
       		;;
    *)
	echo "输入错误！"
	exit 1
	;;
esac
