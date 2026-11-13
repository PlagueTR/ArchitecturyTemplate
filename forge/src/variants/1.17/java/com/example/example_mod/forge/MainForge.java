package com.example.example_mod.forge;

import com.example.example_mod.Main;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.loading.FMLEnvironment;

@Mod(Main.MOD_ID)
public final class MainForge {

    public MainForge() {
        Main.init();

        if (FMLEnvironment.dist == Dist.CLIENT) {
            ClientMainForge.init();
        }
    }

}
