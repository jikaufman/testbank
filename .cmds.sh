#!/bin/bash

function scrape () {
    echo "Input your username"
    read username

    echo "Input your password"
    read -s password

    python scrape.py $username $password
}