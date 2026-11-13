package com.example.example_mod.neoforge;

import com.example.example_mod.Main;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.loading.FMLEnvironment;

@Mod(Main.MOD_ID)
public final class MainNeoForge {

    public MainNeoForge() {
        Main.init();

        if (FMLEnvironment.dist == Dist.CLIENT) {
            ClientMainNeoForge.init();
        }
    }

}
