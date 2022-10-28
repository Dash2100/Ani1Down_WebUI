function download() {
    if($("input").val() == ""){
        toast("error", "Please enter a link");
        return(0);
    }
    $.ajax({
        url: "/getData",
        method: "get",
        success: function (res) {
            if (res["status"] === false) {
                $('#loader').show();
            }
            else {
                $('#loader-waiting').show();
            }
        },
        error: function (res) {
            toast("error", "Something went wrong");
        }
    }).then(function (res) {
        var datas = {
            "url": $("input").val()
        }
        document.getElementById("input").value = "";
        $.ajax({
            url: "/form",
            method: "post",
            data: datas,
            success: function (res) {
                if (res == "URL Error") {
                    toast('error', "URL Error")
                    $('#loader').hide();
                    $('#loader-waiting').hide();
                }
                if (res == "added to queue list") {
                    toast('success', "Added to queue")
                    $('#loader').hide();
                    $('#loader-waiting').hide();
                    getData();
                }
                if (res == "already in downloading") {
                    toast('error', "Already in downloading")
                    $('#loader').hide();
                    $('#loader-waiting').hide();
                }
                if (res == "Download Complete") {
                    toast('success', "Download Complete")
                }
                if (res == "Download Cancel"){
                    toast('error', "Download Cancel")
                }
                if (res == "already in queue") {
                    toast('error', "Already in queue")
                    $('#loader').hide();
                    $('#loader-waiting').hide();
                }
                if (res == "File Exist") {
                    toast('error', "File is already exist")
                    $('#loader').hide();
                    $('#loader-waiting').hide();
                }
            },
            error: function (res) {
                Swal.fire({
                    icon: 'error',
                    title: "Server Error",
                    text: "Please try again later",
                    allowEscapeKey: false,
                    allowOutsideClick: false,
                    showCancelButton: false
                }).then(function (result) {
                    if (result.value) {
                        window.location.reload();
                    }
                });
                $('#loader').hide();
            }
        })
    });
}

function stop() {
    Swal.fire({
        title: 'Stop this task?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: "/stop",
                method: "get",
            })
        }
    })
}

function rmqueue(name) {
    Swal.fire({
        title: 'Delete this task?',
        text: name + " will not be downloaded",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                url: "/rmqueue/" + name,
                method: "get",
                success: function (res) {
                    if (res == "OK") {
                        toast('success', "Deleted!")
                        getData();
                    }
                    if (res == "Not Found") {
                        toast('error', "Not Found")
                    }
                },
                error: function (res) {
                    toast("error", "Something went wrong");
                }
            })
        }
    })
}

function getData() {
    $.ajax({
        url: "/getData",
        method: "get",
        success: function (res) {
            if (Object.keys(res["downloading"])[0] != undefined) {
                if (res["status"] === true) {
                    var list = document.getElementsByClassName("nowdownload")[0];
                    download_div = document.getElementsByClassName("ndownload")[0];
                    if(download_div === undefined){
                        $('#loader').hide();
                        list.innerHTML = `
                        <li class="list-group-item d-flex justify-content-between align-items-start">
                            <div class="ms-2 me-auto">
                                <div class="fw-bold">` + Object.keys(res["downloading"])[0] + '</div>' + "Loading..." + `
                            </div>
                            <i onclick="stop();" class="fa-solid fa-trash"></i>
                        </li>`;
                    }
                }
            }
            if (res["waiting"] != "") {
                $('#loader-waiting').hide();
                var list = document.getElementsByClassName("waitdownload")[0];
                list.innerHTML = String(Object.keys(res["waiting"])).split(",").map((item) => {
                    tname = Object.keys(res["waiting"][item]);
                    strname = "'" + tname + "'";
                    return `
                    <li class="list-group-item d-flex justify-content-between align-items-start">
                        <div class="ms-2 me-auto">
                            <div class="fw-bold">` + tname + `</div>
                        </div>
                        <i onclick="rmqueue(` + strname + `);" class="fa-solid fa-trash"></i>
                    </li>`;
                }).join("");
            }
            else{
                var list = document.getElementsByClassName("waitdownload")[0];
                list.innerHTML = "";
            }
            if (res["status"] === true) {
                if (Object.keys(res["downloading"])[0] === undefined) {
                    $('#loader').show();
                    var list = document.getElementsByClassName("nowdownload")[0];
                    list.innerHTML = '';
                }
            }
            else {
                $('#loader').hide();
                document.getElementsByClassName("nowdownload")[0].innerHTML = '';
                document.getElementsByClassName("waitdownload")[0].innerHTML = '';
            }
        },
        error: function (res) {
            toast("error","API Error");
        }
    })
}

function toast(type, text) {
    const Toast = Swal.mixin({
        toast: true,
        position: 'bottom-right',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
        }
    })

    Toast.fire({
        icon: type,
        title: text
    })
}

function onload(){
    getData();
    var socket = io.connect();
    socket.on('update_data', function(data) {
        utype = data.update_type;
        udata = data.data;
        if(utype==="downloading"){
            $('#loader').hide();
            $('#loader-waiting').hide();
            var list = document.getElementsByClassName("nowdownload")[0];
            list.innerHTML = `
            <li class="list-group-item d-flex justify-content-between align-items-start ndownload">
                <div class="ms-2 me-auto">
                <div class="fw-bold">` + Object.keys(udata)[0] + '</div>' + Object.values(udata)[0] + `</div>
                <i onclick="stop();" class="fa-solid fa-trash"></i>
            </li>
            `;
        }
        if(utype==="notdownloading"){
            $('#loader').hide();
            $('#loader-waiting').hide();
            var list = document.getElementsByClassName("nowdownload")[0];
            list.innerHTML = '';
        }
        if(utype==="getdata"){
            getData();
        }
    });
}