from dataclasses import dataclass


@dataclass(frozen=True)
class QualityProfile:
    name: str
    dir: str
    height: int
    video_bitrate: str
    max_rate: str
    buf_size: str
    bandwidth: int


@dataclass(frozen=True)
class HlsVariant:
    name: str
    dir: str
    bandwidth: int
    width: int
    height: int


QUALITY_PROFILES: list[QualityProfile] = [
    QualityProfile(
        name="144p",
        dir="144",
        height=144,
        video_bitrate="250k",
        max_rate="275k",
        buf_size="550k",
        bandwidth=275_000,
    ),
    QualityProfile(
        name="240p",
        dir="240",
        height=240,
        video_bitrate="500k",
        max_rate="550k",
        buf_size="1100k",
        bandwidth=550_000,
    ),
    QualityProfile(
        name="360p",
        dir="360",
        height=360,
        video_bitrate="800k",
        max_rate="880k",
        buf_size="1760k",
        bandwidth=880_000,
    ),
    QualityProfile(
        name="480p",
        dir="480",
        height=480,
        video_bitrate="1400k",
        max_rate="1540k",
        buf_size="3080k",
        bandwidth=1_540_000,
    ),
    QualityProfile(
        name="720p",
        dir="720",
        height=720,
        video_bitrate="2800k",
        max_rate="3080k",
        buf_size="6160k",
        bandwidth=3_080_000,
    ),
    QualityProfile(
        name="1080p",
        dir="1080",
        height=1080,
        video_bitrate="5000k",
        max_rate="5500k",
        buf_size="11000k",
        bandwidth=5_500_000,
    ),
]
