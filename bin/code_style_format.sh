#!/usr/bin/env bash

dev_proj_abs_path=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

autoflake_cmd="autoflake --remove-all-unused-imports --ignore-init-module-imports -r -i"

isort $dev_proj_abs_path/src
isort $dev_proj_abs_path/bin

black $dev_proj_abs_path/src
black $dev_proj_abs_path/bin

$autoflake_cmd $dev_proj_abs_path/src
$autoflake_cmd $dev_proj_abs_path/bin

cd $dev_proj_abs_path
git add *
git commit -m "style: 💄 format code style"
