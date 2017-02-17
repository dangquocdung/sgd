/*
 * Copyright (c) 2010 Mo Chen <withinsea@gmail.com>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*
 * jQuery Data Extra
 *
 * Depends:
 *	jquery.js 1.3+
 */
if (jQuery && jQuery.data && !jQuery.data.metaKey) (function ($) {

    // extend .data()

    var _data = $.data;

    $.data = function (elem, name, data) {
        var isElem = elem && (elem.nodeType == 1);
        if (isElem && _data(elem, $.data.metaKey) === undefined) {
            var metadata = {};
            var attrs = elem.attributes;
            for (var attrI = 0; attrI < attrs.length; attrI++) {
                var attrname = attrs[attrI].name, attrvalue = attrs[attrI].value;
                if (attrname.match(/^data-/)) {
                    var parts = attrname.substring('data-'.length).split('-');
                    var metaobj = metadata;
                    for (var i = 0; i < parts.length - 1; i++) {
                        metaobj[parts[i]] = (metaobj[parts[i]] && typeof metaobj[parts[i]] == 'object')
                                ? metaobj[parts[i]] : {};
                        metaobj = metaobj[parts[i]];
                    }
                    metaobj[parts[parts.length - 1]] = attrvalue.match(
                            /^\s*(null|undefined|true|false|[+-]?\d+(\.\d+)?|\/[\s\S]*\/|\[[\s\S]*\]|{[\s\S]*\})\s*$/
                    ) ? eval('(' + attrvalue + ')') : attrvalue;
                }
            }
            _data(elem, $.data.metaKey, metadata);
        }
        var data = _data.apply(this, arguments);
        if (data !== undefined || !isElem || typeof name != 'string') {
            return data;
        } else {
            var metadata = _data(elem, $.data.metaKey);
            return (metadata === undefined) ? undefined : eval('metadata.' + name);
        }
    };

    $.extend($.data, {
        metaKey: 'metadata',
        jqueryNamespace: 'jq'
    });

    $(function () {
        // delay to last
        $(function () {
            $('[data.' + $.data.jqueryNamespace + ']').each(function () {
                var self = $(this);
                var jqData = self.data('jq') || {};
                for (var pluginName in jqData) {
                    if ($.fn[pluginName]) {
                        self[pluginName](jqData[pluginName]);
                    }
                }
            });
        });
    });

    // extend data- selector

    var Expr = $.expr, type = 'ATTR', _ATTR_FILTER = $.expr.filter.ATTR;

    Expr.match.ATTR = /\[\s*((?:[\w\u00c0-\uFFFF_-]|\\.)+|data\.(?:[\w\u00c0-\uFFFF_-]|\\.)(?:[\.\w\u00c0-\uFFFF_-]|\\.)*)\s*(?:(\S?=)\s*(['"]*)(.*?)\3|)\s*\]/;
    Expr.match[ type ] = new RegExp(Expr.match[ type ].source + /(?![^\[]*\])(?![^\(]*\))/.source);
    Expr.leftMatch[ type ] = new RegExp(/(^(?:.|\r|\n)*?)/.source + Expr.match[ type ].source.replace(/\\(\d+)/g, function(all, num) {
        return "\\" + (num - 0 + 1);
    }));

    Expr.filter.ATTR = function(elem, match) {

        var name = match[1];
        if (name.indexOf('.') < 0) {
            return _ATTR_FILTER.apply(this, arguments);
        }

        var result = $(elem).data(name.replace(/^data\./, '')) || null,
                value = result + "",
                type = match[2],
                check = match[4];

        return result == null ?
               type === "!=" :
               type === "=" ?
               value === check :
               type === "*=" ?
               value.indexOf(check) >= 0 :
               type === "~=" ?
               (" " + value + " ").indexOf(check) >= 0 :
               !check ?
               value && result !== false :
               type === "!=" ?
               value != check :
               type === "^=" ?
               value.indexOf(check) === 0 :
               type === "$=" ?
               value.substr(value.length - check.length) === check :
               type === "|=" ?
               value === check || value.substr(0, check.length + 1) === check + "-" :
               false;
    };

})(jQuery);
