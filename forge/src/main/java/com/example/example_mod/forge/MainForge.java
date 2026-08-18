package com.example.example_mod.forge;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLEnvironment;

import com.example.example_mod.Main;

@Mod(Main.MOD_ID)
public final class MainForge {
    public MainForge() {

        Main.init();

        if (FMLEnvironment.dist == Dist.CLIENT) {
            new ClientMainForge();
        }

    }
}
