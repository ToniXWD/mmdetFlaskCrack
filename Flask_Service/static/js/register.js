function bindCaptureBtnClick() {
    $("#capture-btn").on("click", function (event) {
        var $this = $(this); //?
        var email = $("input[name='email']").val(); //获取input的邮箱标签,.val()表示获取值
        if (!email) {
            alert("请先输入邮箱!");
            return;
        }
        //    通过js发送网络请求:ajax（Async JavaScript And XML），xml现在一般改成json
        $.ajax({
            url: "/user/validCodes", //发送给user里写的函数
            method: "POST",
            data: {
                "email": email
            },
            success: function (res) { // 若发送成功，返回后执行的函数，res取决于user里写的函数返回的结果
                var code = res['code'];
                if (code == 200) {
                    //取消点击事件
                    $this.off("click");
                    //开始倒计时
                    var countDown = 60;
                    var timer = setInterval(function () {
                        countDown -= 1;
                        if (countDown > 0) {
                            $this.text(countDown + "秒后重新发送");
                        } else {
                            $this.text("获取验证码");
                            bindCaptureBtnClick();
                            clearInterval(timer);
                        }
                    }, 1000);
                    alert("验证码发送成功");
                }
                else if (code == 600){
                    alert("该邮箱已经注册过")
                } else {
                    alert(res['message']);
                }
            }
        })
    }) //绑定按钮
}

$(function () { //等待网页加载完成后再执行
    bindCaptureBtnClick();
});