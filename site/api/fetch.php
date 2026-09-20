<?php
// pkushal.com.np — lab fetch proxy. Modes: og (default) | robots | schema.
// SSRF-hardened: http/https only, private/reserved IPs blocked, DNS pinned,
// size- and time-limited, returns parsed data only (never the raw body wholesale
// except robots.txt, which is public plain text by design).
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

function fail($m, $code = 400) {
    http_response_code($code);
    echo json_encode(['ok' => false, 'error' => $m]);
    exit;
}

$url  = isset($_GET['url'])  ? trim($_GET['url'])  : '';
$mode = isset($_GET['mode']) ? strtolower(trim($_GET['mode'])) : 'og';
if (!in_array($mode, ['og', 'robots', 'schema'], true)) $mode = 'og';
if ($url === '')         fail('Missing url parameter');
if (strlen($url) > 2048) fail('URL too long');

$p = parse_url($url);
if (!$p || empty($p['scheme']) || empty($p['host'])) fail('Invalid URL');
$scheme = strtolower($p['scheme']);
if ($scheme !== 'http' && $scheme !== 'https') fail('Only http/https is allowed');
$host = $p['host'];
$port = isset($p['port']) ? (int)$p['port'] : ($scheme === 'https' ? 443 : 80);

$ips = filter_var($host, FILTER_VALIDATE_IP) ? [$host] : @gethostbynamel($host);
if (!$ips) fail('Host does not resolve', 502);
foreach ($ips as $ip) {
    if (!filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
        fail('Blocked: private or reserved address', 403);
    }
}
$pin = $ips[0];

if ($mode === 'robots') {
    $portpart = ($port && $port != 80 && $port != 443) ? ':' . $port : '';
    $target = $scheme . '://' . $host . $portpart . '/robots.txt';
} else {
    $target = $url;
}

function do_fetch($target, $host, $pin, $max = 524288) {
    $buf = '';
    $ch = curl_init($target);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER  => true,
        CURLOPT_FOLLOWLOCATION  => true,
        CURLOPT_MAXREDIRS       => 3,
        CURLOPT_TIMEOUT         => 8,
        CURLOPT_CONNECTTIMEOUT  => 5,
        CURLOPT_USERAGENT       => 'pkushal.com.np lab bot (+https://pkushal.com.np)',
        CURLOPT_SSL_VERIFYPEER  => true,
        CURLOPT_PROTOCOLS       => CURLPROTO_HTTP | CURLPROTO_HTTPS,
        CURLOPT_REDIR_PROTOCOLS => CURLPROTO_HTTP | CURLPROTO_HTTPS,
        CURLOPT_RESOLVE         => ["$host:80:$pin", "$host:443:$pin"],
        CURLOPT_WRITEFUNCTION   => function ($c, $data) use (&$buf, $max) {
            $buf .= $data;
            if (strlen($buf) > $max) return -1;
            return strlen($data);
        },
    ]);
    curl_exec($ch);
    $err   = curl_error($ch);
    $code  = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $final = curl_getinfo($ch, CURLINFO_EFFECTIVE_URL);
    curl_close($ch);
    return [$buf, $code, $final, $err];
}

list($buf, $code, $final, $err) = do_fetch($target, $host, $pin);

if ($mode === 'robots') {
    echo json_encode([
        'ok' => true, 'mode' => 'robots', 'status' => $code, 'final_url' => $final,
        'robots' => substr($buf, 0, 524288),
    ], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    exit;
}

if ($buf === '') fail('Fetch failed' . ($err ? ': ' . $err : ''), 502);
$html = substr($buf, 0, 524288);

if ($mode === 'schema') {
    $blocks = [];
    $types  = [];
    if (preg_match_all('/<script[^>]+type=["\']application\/ld\+json["\'][^>]*>(.*?)<\/script>/is', $html, $mm)) {
        foreach ($mm[1] as $b) {
            $b = trim(html_entity_decode($b, ENT_QUOTES | ENT_HTML5));
            if ($b !== '') $blocks[] = $b;
        }
    }
    if (preg_match_all('/"@type"\s*:\s*"([^"]+)"/', $html, $tm)) {
        $types = array_values(array_unique($tm[1]));
    }
    echo json_encode([
        'ok' => true, 'mode' => 'schema', 'status' => $code, 'final_url' => $final,
        'count' => count($blocks), 'types' => $types, 'blocks' => $blocks,
    ], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    exit;
}

// mode = og (default)
function meta($html, $prop) {
    $q = preg_quote($prop, '/');
    if (preg_match('/<meta[^>]+(?:property|name)=["\']' . $q . '["\'][^>]+content=["\']([^"\']*)["\']/i', $html, $m))
        return html_entity_decode($m[1], ENT_QUOTES | ENT_HTML5);
    if (preg_match('/<meta[^>]+content=["\']([^"\']*)["\'][^>]+(?:property|name)=["\']' . $q . '["\']/i', $html, $m))
        return html_entity_decode($m[1], ENT_QUOTES | ENT_HTML5);
    return '';
}
$title = '';
if (preg_match('/<title[^>]*>(.*?)<\/title>/is', $html, $m)) $title = trim(html_entity_decode($m[1], ENT_QUOTES | ENT_HTML5));
$canon = '';
if (preg_match('/<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']*)["\']/i', $html, $m)) $canon = $m[1];

echo json_encode([
    'ok' => true, 'mode' => 'og', 'status' => $code, 'final_url' => $final,
    'title'        => meta($html, 'og:title') ?: $title,
    'description'  => meta($html, 'og:description') ?: meta($html, 'description'),
    'canonical'    => meta($html, 'og:url') ?: $canon,
    'image'        => meta($html, 'og:image'),
    'site_name'    => meta($html, 'og:site_name'),
    'type'         => meta($html, 'og:type'),
    'twitter_card' => meta($html, 'twitter:card'),
    'twitter_site' => meta($html, 'twitter:site'),
], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
