FormUtils = {
    setNextElement: function () {
        $(".cls_element").unbind("keypress");
        $(".cls_element").keypress(function (k) {
            if (k.keyCode == 13) {
                var fields = $(this).parents('.form').find('.cls_element');
                var index = fields.index(this);
                //console.log(index);
                //console.log($(this).closest(".input").next("div.input").first().html());
                //console.log($(this).closest(".input").next(".input").html());
                if (index > -1 && (index + 1) < fields.length) {
                    $('.cls_element', '.form').removeClass("backgroundfocus");
                    fields.eq(index + 1).focus();
                    fields.eq(index + 1).addClass("backgroundfocus");
                }
                //                if ($(this).closest(".input").next().find(".cls_element").length > 0) {
                //                    console.log("có");
                //                    $(this).closest(".input").next().find(".cls_element").focus();
                //                }
                //                else {
                //                    console.log("không có");
                //                    $(this).closest(".field").next().find(".cls_element").focus();
                //                }
            }
        });
        $(".cls_element", '.form').unbind("focusout");
        $(".cls_element", '.form').focusout(function () {
            $(this).removeClass("backgroundfocus");
        });
        $(".ui-state-default").unbind("hover");
        $(".ui-state-default").hover(function () {
            $(this).addClass('ui-state-hover');
        }, function () {
            $(this).removeClass('ui-state-hover');
        });
    },
    getAlias: function (plainText) {
        var _URL_CHARS_UNICODE = "AÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴBCDĐEÉÈẸẺẼÊẾỀỆỂỄFGHIÍÌỊỈĨJKLMNOÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠPQRSTUÚÙỤỦŨƯỨỪỰỬỮVWXYÝỲỴỶỸZaáàạảãâấầậẩẫăắằặẳẵbcdđeéèẹẻẽêếềệểễfghiíìịỉĩjklmnoóòọỏõôốồộổỗơớờợởỡpqrstuúùụủũưứừựửữvwxyýỳỵỷỹz0123456789_";
        var _URL_CHARS_ANSI = "AAAAAAAAAAAAAAAAAABCDDEEEEEEEEEEEEFGHIIIIIIJKLMNOOOOOOOOOOOOOOOOOOPQRSTUUUUUUUUUUUUVWXYYYYYYZaaaaaaaaaaaaaaaaaabcddeeeeeeeeeeeefghiiiiiijklmnoooooooooooooooooopqrstuuuuuuuuuuuuvwxyyyyyyz0123456789_";
        var _URL_CHARS_BASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_";
        var _strTemp = "";
        var _iLength = plainText.length;
        var _iIndex = 0;
        // Loại bỏ các ký tự có dấu
        for (var i = 0; i < _iLength; i++) {
            iIndex = _URL_CHARS_UNICODE.indexOf(plainText.charAt(i));
            if (iIndex == -1)
                _strTemp += plainText.charAt(i);
            else
                _strTemp += _URL_CHARS_ANSI.charAt(iIndex);
        }
        var _strReturn = "";

        _iLength = _strTemp.length;
        // Loại bỏ các ký tự lạ
        for (var i1 = 0; i1 < _iLength; i1++) {
            if (_URL_CHARS_BASE.indexOf(_strTemp.charAt(i1)) == -1) {
                _strReturn += '';
            }
            else {
                _strReturn += _strTemp.charAt(i1);
            }
        }

        while (_strReturn.indexOf("--") != -1) {
            _strReturn = _strReturn.replace('--', '');
        }

        if ((_strReturn.length > 0) && (_strReturn.charAt(0) == '-')) {
            _strReturn = _strReturn.substr(1);
        }

        if ((_strReturn.length > 0) && (_strReturn.charAt(_strReturn.length - 1) == '-')) {
            _strReturn = _strReturn.substr(0, _strReturn.length - 1);
        }
        if (_strReturn.length > 60) {
            _iIndex = _strReturn.indexOf('-', 59);
            if (_iIndex != -1) {
                _strReturn = _strReturn.substring(0, _iIndex);
            }
        }
        return _strReturn.toLowerCase();
    },
    isEnterNumber: function (evt, _arrCode) {
        // Chỉ cho nhập vào các kí tự từ 0 => 9, del,tab
        var keyCode = evt.keyCode ? evt.keyCode : evt.which;
        //console.log(keyCode);
        var arrCode = new Array(13, 37, 39, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 8, 9, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 35, 36);
        if (_arrCode != undefined)
            arrCode = arrCode.concat(_arrCode);
        if ($.browser.msie) {
            for (var i = 0; i < arrCode.length; i++) {
                if (arrCode[i] == keyCode) {
                    return true;
                    break;
                }
            }
            return false;
        }
        else {
            if (arrCode.indexOf(keyCode) > -1) return true;
            return false;
        }
    },
    isValidDate: function (dateString) {
        // First check for the pattern
        if (!/^\d{1,2}\/\d{1,2}\/\d{4}$/.test(dateString))
            return false;
        // Parse the date parts to integers
        var parts = dateString.split("/");
        var day = parseInt(parts[0], 10);
        var month = parseInt(parts[1], 10);
        var year = parseInt(parts[2], 10);

        // Check the ranges of month and year
        if (year < 1000 || year > 3000 || month == 0 || month > 12)
            return false;

        var monthLength = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

        // Adjust for leap years
        if (year % 400 == 0 || (year % 100 != 0 && year % 4 == 0))
            monthLength[1] = 29;

        // Check the range of the day
        return day > 0 && day <= monthLength[month - 1];
    },
    setActionAmount: function () {
        $(".clsPrice").SetInputPrice();
    }
};
$(function (parameters) {
    $(".aContextFunction").live('click', function () {
        var m_div = $(".divContextFunction", $(this).parent());
        var _width = $(this).outerWidth();
        var cur = $(m_div).is(':visible');
        var width = $(m_div).outerWidth();
        $(m_div).css("left", ($(this).offset().left - (width - _width)) + "px");
        $(m_div).css("top", $(this).offset().top + 26 + "px");
        $('.divContextFunction:visible').hide();
        if (cur)
            $(m_div).hide();
        else
            $(m_div).show();
    });
    $(document).click(function (event) {
        if ($('.divContextFunction').is(':visible') && !$(event.target).closest(".aContextFunction").size()) {
            $('.divContextFunction').hide();
        }
    });
    $(".ui-state-default").hover(function () {
        $(this).addClass('ui-state-hover');
    }, function () {
        $(this).removeClass('ui-state-hover');
    });

});
/*Set định dạng tiền tệ cho đối tượng*/
$.fn.SetInputPrice = function () {
    this.options =
    {
        amount: 3,
        seperator: ','
    };
    var inputPrice = this;
    $(this).css("text-align", "right");
    $(this).focus(function () { this.select(); });
    $(this).mouseup(function (e) { e.preventDefault(); });
    $(this).keydown(function (evt) {
        return FormUtils.isEnterNumber(evt);
    });
    $(this).keyup(function (k) {
        inputPrice.formatPrice(this);
    });
    this.formatPrice = function (price) {
        var val = $(price).val();
        val = inputPrice.convertMoney(val);
        $(price).val(val);
    };
    this.convertMoney = function (data) {
        var _data = data + "";
        var _objectData = _data.split(inputPrice.options.seperator);
        var _newData = "";
        _data = "";
        for (var i = 0; i < _objectData.length; i++) {
            if (i == 0 && _objectData[i] != 0)
                _data += _objectData[i];
            if (i > 0)
                _data += _objectData[i];
        }
        if (_data.indexOf("0") == 0)
            _data = _data.substr(1);
        var j = 0;
        for (var i = _data.length - 1; i >= 0; i--) {
            if ((j % inputPrice.options.amount == 0) && j > 2)
                _newData = inputPrice.options.seperator + _newData;
            _newData = _data[i] + _newData;
            j++;
        }
        if (_newData.length == 0) _newData = 0;
        return _newData;
    };
    return inputPrice;
};
//Lấy giá trị của một đối tượng có định dạng tiền tệ
$.fn.getPriceValue = function () {
    var priceValue = this;
    var val = 0;
    this.getMoney = function (data) {
        try {
            var _data = data + "";
            if (_data.length == 0)
                return 0;
            var _objectData = _data.split(",");
            var _newData = "";
            _data = "";
            for (var i = 0; i < _objectData.length; i++) {
                _data += _objectData[i];
            }
            for (var i = _data.length - 1; i >= 0; i--) {
                _newData = _data[i] + _newData;
            }
            return eval(_newData);
        } catch (ex) {
            return 0;
        }
    };
    if ($(priceValue).is("input") || $(priceValue).is("select")) {
        val = priceValue.getMoney($.trim($(priceValue).val()));
    }
    if ($(priceValue).is("span") || $(priceValue).is("div") || $(priceValue).is("td") || $(priceValue).is("label")) {
        val = priceValue.getMoney($.trim($(priceValue).html()));
    }
    return eval(val);
};