import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)
DOMAIN = "bilibili_fans"
SCAN_INTERVAL = timedelta(hours=1)  # 每小时更新一次

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Set up the Bilibili Fans sensor from yaml configuration."""
    if discovery_info is not None:
        vmid = discovery_info["vmid"]
        name = discovery_info.get("name")
    else:
        vmid = config.get("vmid")
        name = config.get("name")
    
    if vmid:
        coordinator = BilibiliDataUpdateCoordinator(hass, vmid)
        await coordinator.async_refresh()
        async_add_entities([BilibiliFansSensor(coordinator, vmid, name)], True)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Bilibili Fans sensor from config entry."""
    vmid = config_entry.data["vmid"]
    name = config_entry.data.get("name")
    coordinator = BilibiliDataUpdateCoordinator(hass, vmid)
    # 直接使用async_refresh而不是async_config_entry_first_refresh，避免ConfigEntryNotReady
    await coordinator.async_refresh()
    async_add_entities([BilibiliFansSensor(coordinator, vmid, name)], True)

class BilibiliDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, vmid):
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.vmid = vmid
        self.hass = hass
        # 初始化存储
        if "bilibili_fans_data" not in hass.data:
            hass.data["bilibili_fans_data"] = {}
        if vmid not in hass.data["bilibili_fans_data"]:
            hass.data["bilibili_fans_data"][vmid] = {
                "last_follower": 0,
                "month_start_follower": 0,
                "year_start_follower": 0,
                "last_update_month": datetime.now().month,
                "last_update_year": datetime.now().year
            }

    async def _async_update_data(self):
        url = f"https://api.bilibili.com/x/relation/stat?vmid={self.vmid}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, ssl=False) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching data: {response.status}")
                data = await response.json()
                if data["code"] != 0:
                    raise UpdateFailed(f"API error: {data['message']}")
                
                # 获取当前数据
                current_data = data["data"]
                follower = current_data["follower"]
                
                # 管理存储的数据
                storage = self.hass.data["bilibili_fans_data"][self.vmid]
                now = datetime.now()
                
                # 检查是否需要重置月统计
                if now.month != storage["last_update_month"]:
                    storage["month_start_follower"] = storage["last_follower"]
                    storage["last_update_month"] = now.month
                
                # 检查是否需要重置年统计
                if now.year != storage["last_update_year"]:
                    storage["year_start_follower"] = storage["last_follower"]
                    storage["last_update_year"] = now.year
                
                # 计算新增粉丝
                monthly_increase = follower - storage["month_start_follower"]
                yearly_increase = follower - storage["year_start_follower"]
                
                # 更新存储
                storage["last_follower"] = follower
                
                # 返回完整数据
                return {
                    "follower": follower,
                    "following": current_data["following"],
                    "mid": current_data["mid"],
                    "monthly_increase": monthly_increase,
                    "yearly_increase": yearly_increase,
                    "month_start_follower": storage["month_start_follower"],
                    "year_start_follower": storage["year_start_follower"]
                }

class BilibiliFansSensor(SensorEntity):
    def __init__(self, coordinator, vmid, name=None):
        self.coordinator = coordinator
        self.vmid = vmid
        self._attr_name = name if name else f"Bilibili Fans {vmid}"
        self._attr_unique_id = f"bilibili_fans_{vmid}"
        self._attr_icon = "mdi:account-group"
        
    @property
    def state(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data["follower"]
    
    @property
    def extra_state_attributes(self):
        if self.coordinator.data is None:
            return {}
        return {
            "following": self.coordinator.data["following"],
            "mid": self.coordinator.data["mid"],
            "monthly_increase": self.coordinator.data["monthly_increase"],
            "yearly_increase": self.coordinator.data["yearly_increase"],
            "month_start_follower": self.coordinator.data["month_start_follower"],
            "year_start_follower": self.coordinator.data["year_start_follower"]
        }
    
    @property
    def available(self):
        return self.coordinator.data is not None
    
    @property
    def native_unit_of_measurement(self):
        return ""
    
    async def async_update(self):
        await self.coordinator.async_request_refresh()
    
    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )