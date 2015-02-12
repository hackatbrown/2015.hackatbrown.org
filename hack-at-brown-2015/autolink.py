import re
from itertools import starmap

import six



PROTOCOLS = ['ed2k', 'ftp', 'http', 'https', 'irc',
             'news', 'gopher', 'nntp', 'telnet', 'webcal',
             'xmpp', 'callto', 'feed', 'urn', 'aim', 'rsync', 'tag',
             'ssh', 'sftp', 'rtsp', 'afs']

TLDS = """ac ad ae aero af ag ai al am an ao aq ar arpa as asia at au aw ax az
       ba bb bd be bf bg bh bi biz bj bm bn bo br bs bt bv bw by bz ca cat
       cc cd cf cg ch ci ck cl cm cn co com coop cr cu cv cx cy cz de dj dk
       dm do dz ec edu ee eg er es et eu fi fj fk fm fo fr ga gb gd ge gf gg
       gh gi gl gm gn gov gp gq gr gs gt gu gw gy hk hm hn hr ht hu id ie il
       im in info int io iq ir is it je jm jo jobs jp ke kg kh ki km kn kp
       kr kw ky kz la lb lc li lk lr ls lt lu lv ly ma mc md me mg mh mil mk
       ml mm mn mo mobi mp mq mr ms mt mu museum mv mw mx my mz na name nc ne
       net nf ng ni nl no np nr nu nz om org pa pe pf pg ph pk pl pm pn pr pro
       ps pt pw py qa re ro rs ru rw sa sb sc sd se sg sh si sj sk sl sm sn so
       sr st su sv sy sz tc td tel tf tg th tj tk tl tm tn to tp tr travel tt
       tv tw tz ua ug uk us uy uz va vc ve vg vi vn vu wf ws xn ye yt yu za zm
       zw""".split()

TLDS.reverse()

url_re = r"""\(*  # Match any opening parentheses.
    \b(?<![@.])(?:(?:{0}):/{{0,3}}(?:(?:\w+:)?\w+@)?)?  # http://
    ([\w-]+\.)+(?:{1})(?:\:\d+)?(?!\.\w)\b   # xx.yy.tld(:##)?
    (?:[/?][^\s\{{\}}\|\\\^\[\]`<>"]*)?
        # /path/zz (excluding "unsafe" chars from RFC 1738,
        # except for # and ~, which happen in practice)
    """.format('|'.join(PROTOCOLS), '|'.join(TLDS))

proto_re = re.compile(r'^[\w-]+:/{0,3}', re.IGNORECASE)

punct_re = re.compile(r'([\.,]*)$')

email_re = r"""(?<!//|.:)(mailto:)?
    \b(([-!#$%&'*+/=?^_`{0!s}|~0-9A-Z]+
        (\.[-!#$%&'*+/=?^_`{1!s}|~0-9A-Z]+)*  # dot-atom
    |^"([\001-\010\013\014\016-\037!#-\[\]-\177]
        |\\[\001-011\013\014\016-\177])*"  # quoted-string
    )@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6})\.?  # domain
    """

combined_re = re.compile("(?P<url>{0})|(?P<email>{1})".format(url_re, email_re),
                         re.IGNORECASE | re.MULTILINE | re.VERBOSE | re.UNICODE)


def linkify(text, attrs={}):
    """
    Convert URL-like and email-like strings into links.
    """
    def separate_parentheses(s):
        start = re_find(r'^\(*', s)
        end = re_find(r'\)*$', s)
        n = min(len(start), len(end))
        if n:
            return s[:n], s[n:-n], s[-n:]
        else:
            return '', s, ''

    def link_repl(url, proto='http://'):
        opening, url, closing = separate_parentheses(url)

        punct = re_find(punct_re, url)
        if punct:
            url = url[:-len(punct)]

        if re.search(proto_re, url):
            href = url
        else:
            href = proto + url
        href = escape_url(href)

        repl = u'{0!s}<a href="{1!s}"{2!s}>{3!s}</a>{4!s}{5!s}'
        return repl.format(opening,
                           href, attrs_text, url, punct,
                           closing)

    def repl(match):
        matches = match.groupdict()
        if matches['url']:
            return link_repl(matches['url'])
        else:
            return link_repl(matches['email'], proto='mailto:')

    # Prepare attrs
    attr = ' {0!s}="{1!s}"'
    attrs_text = ''.join(starmap(attr.format, attrs.items()))

    # Make replaces
    return re.sub(combined_re, repl, force_unicode(text))


def escape_url(url):
    return url.replace('&', '&amp;')


def force_unicode(s, encoding='utf-8', errors='strict'):
    """
    Similar to smart_text, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.
    """
    # Handle the common case first, saves 30-40% when s is an instance of
    # six.text_type. This function gets called often in that setting.
    if isinstance(s, six.text_type):
        return s
    if not isinstance(s, six.string_types):
        if six.PY3:
            if isinstance(s, bytes):
                s = six.text_type(s, encoding, errors)
            else:
                s = six.text_type(s)
        else:
            s = six.text_type(bytes(s), encoding, errors)
    else:
        # Note: We use .decode() here, instead of six.text_type(s,
        # encoding, errors), so that if s is a SafeBytes, it ends up being
        # a SafeText at the end.
        s = s.decode(encoding, errors)
    return s


def re_find(regex, s):
    m = re.search(regex, s)
    if m:
        return m.group()
